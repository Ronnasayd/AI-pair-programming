from legacy.backups.my_mcp_server import my_search_references

if __name__ == "__main__":
    from pprint import pprint

    # result = my_convert_tasks_to_markdown(
    #     rootProject="$HOME/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_search_references(
        query="create event bulk",
        rootProject="$HOME/develop/lingopass/lingospace-backend",
    )
    # result = run_text_command(
    #     "create event bulk","$HOME/develop/lingopass/lingospace-backend",["$HOME/develop/lingopass/lingospace-backend/src/modules/event/*.ts"]
    # )
    print(result)
