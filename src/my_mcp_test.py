from my_mcp_server import my_convert_markdown_to_tasks, my_convert_tasks_to_markdown

if __name__ == "__main__":
    # result = my_convert_tasks_to_markdown(
    #     cwd="/home/ronnas/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_convert_markdown_to_tasks(cwd="/home/ronnas/develop/lingopass/lingospace-backend")
    print(result)
