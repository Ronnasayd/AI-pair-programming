from my_mcp_server import my_get_context

if __name__ == "__main__":
    # result = my_convert_tasks_to_markdown(
    #     rootProject="/home/ronnas/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_get_context(
        exclude="",
        exclude_content="",
        include="",
        llist=False,
        paths=["/home/ronnas/develop/personal/AI-pair-programming/src"],
        text="ollama",
        text_full=False,
        tree=False,
        workers="",
    )
    print(result)
