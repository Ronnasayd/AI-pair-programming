from my_mcp_server import my_search_references

if __name__ == "__main__":
    # result = my_convert_tasks_to_markdown(
    #     rootProject="/home/ronnas/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_search_references(
        query="token image",
        rootProject="/home/ronnas/develop/lingopass/lingospace-backend",
    )
    print(result)
