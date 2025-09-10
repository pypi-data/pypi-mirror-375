import timeit
from argparse import Namespace
from user_sim.cli.cli import parse_chat_arguments
from user_sim.core.data_extraction import DataExtraction
from user_sim.core.role_structure import *
from user_sim.core.user_simulator import UserSimulator
from user_sim.utils.show_logs import *
from user_sim.utils.utilities import *
from user_sim.utils import config
from user_sim.utils.token_cost_calculator import create_cost_dataset
from user_sim.utils.register_management import clean_temp_files
from chatbot_connectors.cli import ChatbotFactory, parse_connector_params
from importlib.resources import files
# check_keys(["OPENAI_API_KEY"])

def configure_project(project_path):
    # sensei
    config.cache_path = files("data") / "cache"
    config.pdfs_path = files("data") / "pdfs"
    config.audio_files_path = files("data") / "audio_files"
    config.default_types_path = files("config") / "types"
    config.default_personalities_path = files("config") / "personalities"

    # project
    config.project_folder_path = project_path
    config.profiles_path = os.path.join(project_path, "profiles")
    config.custom_personalities_path = os.path.join(project_path, "personalities")
    config.custom_types_path = os.path.join(project_path, "types")
    custom_types = load_yaml_files_from_folder(config.custom_types_path)


    default_types = load_yaml_files_from_folder(config.default_types_path, existing_keys=custom_types.keys())
    config.types_dict = {**default_types, **custom_types}


def _setup_configuration() -> Namespace:
    """Parse command line arguments, validate config, and create output dir.

    Returns:
        The parsed and validated command line arguments

    Raises:
        TracerError: If the specified technology is invalid
    """

    args = parse_chat_arguments()

    logger = create_logger(args.verbose, 'Info Logger')
    logger.info('Logs enabled!')

    configure_project(args.project_path)

    # check_keys(["OPENAI_API_KEY"])
    config.test_cases_folder = args.output
    config.ignore_cache = args.ignore_cache
    config.update_cache = args.update_cache
    config.clean_cache = args.clean_cache

    return args


def get_conversation_metadata(user_profile, the_user, serial=None):
    def conversation_metadata(up):
        interaction_style_list = []
        conversation_list = []

        for inter in up.interaction_styles:
            interaction_style_list.append(inter.get_metadata())

        conversation_list.append({'interaction_style': interaction_style_list})

        if isinstance(up.yaml['conversation']['number'], int):
            conversation_list.append({'number': up.yaml['conversation']['number']})
        else:
            conversation_list.append({'number': up.conversation_number})

        if 'random steps' in up.yaml['conversation']['goal_style']:
            conversation_list.append({'goal_style': {'steps': up.goal_style[1]}})
        else:
            conversation_list.append(up.yaml['conversation']['goal_style'])

        return conversation_list


    def ask_about_metadata(up):
        if not up.ask_about.variable_list:
            return up.ask_about.str_list

        if user_profile.ask_about.picked_elements:
            user_profile.ask_about.picked_elements = [
        {clave: (valor[0] if isinstance(valor, list) and len(valor) == 1 else valor)
         for clave, valor in dic.items()}
        for dic in user_profile.ask_about.picked_elements
    ]

        return user_profile.ask_about.str_list + user_profile.ask_about.picked_elements

    def data_output_extraction(u_profile, user):
        output_list = u_profile.output
        data_list = []
        for output in output_list:
            var_name = list(output.keys())[0]
            var_dict = output.get(var_name)
            my_data_extract = DataExtraction(user.conversation_history,
                                             var_name,
                                             var_dict["type"],
                                             var_dict["description"])
            data_list.append(my_data_extract.get_data_extraction())

        data_dict = {k: v for dic in data_list for k, v in dic.items()}
        has_none = any(value is None for value in data_dict.values())
        if has_none:
            count_none = sum(1 for value in data_dict.values() if value is None)
            config.errors.append({1001: f"{count_none} goals left to complete."})

        return data_list

    def total_cost_calculator():
        import pandas as pd
        encoding = get_encoding(config.cost_ds_path)["encoding"]
        cost_df = pd.read_csv(config.cost_ds_path, encoding=encoding)
        total_sum_cost = cost_df[cost_df["Conversation"]==config.conversation_name]['Total Cost'].sum()
        total_sum_cost = round(float(total_sum_cost), 8)

        return total_sum_cost


    data_output = {'data_output': data_output_extraction(user_profile, the_user)}
    context = {'context': user_profile.raw_context}
    ask_about = {'ask_about': ask_about_metadata(user_profile)}
    conversation = {'conversation': conversation_metadata(user_profile)}
    language = {'language': user_profile.language}
    serial_dict = {'serial': serial}
    errors_dict = {'errors': config.errors}
    total_cost = {'total_cost($)': total_cost_calculator()}
    metadata = {**serial_dict,
                **language,
                **context,
                **ask_about,
                **conversation,
                **data_output,
                **errors_dict,
                **total_cost
                }

    return metadata


def build_chatbot(technology, connector):
    parsed_connector = parse_connector_params(connector)
    chatbot = ChatbotFactory.create_chatbot(chatbot_type=technology, **parsed_connector)
    return chatbot


def generate_conversation(technology, connector, user,
                          personality, output, project_folder):
    profiles = parse_profiles(user)
    serial = generate_serial()
    config.serial = serial
    create_cost_dataset(serial, output)
    my_execution_stat = ExecutionStats(output, serial)
    the_chatbot = build_chatbot(technology, connector)


    for profile in profiles:
        user_profile = RoleData(profile, project_folder, personality)
        test_name = user_profile.test_name
        config.test_name = test_name
        chat_format = user_profile.format_type
        start_time_test = timeit.default_timer()

        for i in range(user_profile.conversation_number):
            config.conversation_name = f'{i}_{test_name}_{serial}.yml'
            the_chatbot.fallback = user_profile.fallback
            the_user = UserSimulator(user_profile, the_chatbot)
            bot_starter = user_profile.is_starter
            response_time = []

            start_time_conversation = timeit.default_timer()
            response = ''

            if chat_format == "speech":
                from user_sim.handlers.asr_module import STTModule

                stt = STTModule(user_profile.format_config)

                def send_user_message(user_msg):
                    print_user(user_msg)
                    stt.say(user_msg)

                def get_chatbot_response(user_msg):
                    start_response_time = timeit.default_timer()
                    is_ok, response = stt.hear()
                    end_response_time = timeit.default_timer()
                    time_sec = timedelta(seconds=end_response_time - start_response_time).total_seconds()
                    response_time.append(time_sec)
                    return is_ok, response

                def get_chatbot_starter_response():
                    is_ok, response = stt.hear()
                    return is_ok, response

            else:

                if user_profile.format_config:
                    logger.warning("Chat format is text, but an SR configuration was provided. This configuration will"
                                   " be ignored.")

                def send_user_message(user_msg):
                    print_user(user_msg)

                def get_chatbot_response(user_msg):
                    start_response_time = timeit.default_timer()
                    is_ok, response = the_chatbot.execute_with_input(user_msg)
                    end_response_time = timeit.default_timer()
                    time_sec = timedelta(seconds=end_response_time - start_response_time).total_seconds()
                    response_time.append(time_sec)
                    return is_ok, response

                def get_chatbot_starter_response():
                    is_ok, response = the_chatbot.execute_starter_chatbot()
                    return is_ok, response

            start_loop = True
            if bot_starter:
                is_ok, response = get_chatbot_starter_response()
                if not is_ok:
                    if response is not None:
                        the_user.update_history("Assistant", "Error: " + response)
                    else:
                        the_user.update_history("Assistant", "Error: The server did not respond.")
                    start_loop = False
                print_chatbot(response)
                user_msg = the_user.open_conversation()
                if user_msg == "exit":
                    start_loop = False

            else:
                user_msg = the_user.open_conversation()
                if user_msg == "exit":
                    start_loop = False
                else:
                    send_user_message(user_msg)
                    is_ok, response = get_chatbot_response(user_msg)
                    if not is_ok:
                        if response is not None:
                            the_user.update_history("Assistant", "Error: " + response)
                        else:
                            the_user.update_history("Assistant", "Error: The server did not respond.")
                        start_loop = False
                    else:
                        print_chatbot(response)

            if start_loop:
                while True:
                    user_msg = the_user.get_response(response)
                    if user_msg == "exit":
                        break
                    send_user_message(user_msg)
                    is_ok, response = get_chatbot_response(user_msg)
                    if response == 'timeout':
                        break
                    print_chatbot(response)
                    if not is_ok:
                        if response is not None:
                            the_user.update_history("Assistant", "Error: " + response)
                        else:
                            the_user.update_history("Assistant", "Error: The server did not respond.")
                        break

            if output:
                end_time_conversation = timeit.default_timer()
                conversation_time = end_time_conversation - start_time_conversation
                formatted_time_conv = timedelta(seconds=conversation_time).total_seconds()
                print(f"Conversation Time: {formatted_time_conv} (s)")

                history = the_user.conversation_history
                metadata = get_conversation_metadata(user_profile, the_user, serial)
                dg_dataframe = the_user.data_gathering.gathering_register
                csv_extraction = the_user.goal_style[1] if the_user.goal_style[0] == 'all_answered' else False
                answer_validation_data = (dg_dataframe, csv_extraction)
                save_test_conv(history, metadata, test_name, output, serial,
                               formatted_time_conv, response_time, answer_validation_data, counter=i)

            config.total_individual_cost = 0
            user_profile.reset_attributes()

            if hasattr(the_chatbot, 'id'):
                the_chatbot.id = None

        end_time_test = timeit.default_timer()
        execution_time = end_time_test - start_time_test
        formatted_time = timedelta(seconds=execution_time).total_seconds()
        print(f"Execution Time: {formatted_time} (s)")
        print('------------------------------')

        if user_profile.conversation_number > 0:
            my_execution_stat.add_test_name(test_name)
            my_execution_stat.show_last_stats()

    if config.clean_cache:
        clean_temp_files()

    if output and len(my_execution_stat.test_names) == len(profiles):
        my_execution_stat.show_global_stats()
        my_execution_stat.export_stats()
    elif output:
        logger.warning("Stats export was enabled but couldn't retrieve all stats. No stats will be exported.")
    else:
        pass

    end_alarm()


def main():
    args = _setup_configuration()
    # try:
    generate_conversation(
        technology = args.technology,
        connector = args.connector_params,
        user = os.path.join(config.profiles_path, args.user_profile),
        personality = None, #todo: check this
        output = args.output,
        project_folder = args.project_path
    )
    # except Exception as e:
    #     logger.error(f"An error occurred while generating the conversation: {e}")


if __name__ == '__main__':
    main()