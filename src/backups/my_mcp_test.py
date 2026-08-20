from my_mcp_server import my_search_references

if __name__ == "__main__":
    from pprint import pprint

    # result = my_convert_tasks_to_markdown(
    #     rootProject="/home/ronnas/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_search_references(
        query="create event bulk",
        rootProject="/home/ronnas/develop/lingopass/lingospace-backend",
    )
    # result = run_text_command(
    #     "create event bulk","/home/ronnas/develop/lingopass/lingospace-backend",["/home/ronnas/develop/lingopass/lingospace-backend/src/modules/event/*.ts"]
    # )
    print(result)
