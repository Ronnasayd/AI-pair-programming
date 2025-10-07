from my_mcp_server import my_run_command

if __name__ == "__main__":
    # result = my_convert_tasks_to_markdown(
    #     rootProject="/home/ronnas/develop/lingopass/lingospace-backend"
    # )
    # print(result)

    result = my_run_command(
        command="python get_size_tokens.py /home/ronnas/develop/personal/AI-pair-programming/src/my_mcp_server.py",
        rootProject="/home/ronnas/develop/personal/AI-pair-programming/src/",
    )
    print(result)
