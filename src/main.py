import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()
uploaded_files = openai.files.list().data
required_file_ids = []

# 사용자 입력
user_content =  input("물어볼꺼:")

# 설계문서들
folder_path = "../resources"
for table_info_filename in os.listdir(folder_path):
    path = os.path.join(folder_path, table_info_filename)
    if os.path.isfile(path): # 파일이면
        file = next((f for f in uploaded_files if f.filename == table_info_filename), None)
        if file == None: # 파일 안올라가있으면
            table_info_file = open(f"{folder_path}/{table_info_filename}", "rb")
            file = client.files.create( # 올림
                file = table_info_file,
                purpose="assistants"
            )
            table_info_file.close()
        required_file_ids.append(file.id)

# # liquibase.yaml
# changelog_filename = "liquibase-player.json"

# # 파일 있는지 확인
# file = next((f for f in uploaded_files if f.filename == changelog_filename), None)

# if file == None: # 파일 없으면 업로드
#     changelog_file = open(f"../{changelog_filename}", "rb")
#     file = client.files.create(
#         file=changelog_file,
#         purpose="assistants"
#     )
#     changelog_file.close()
# required_file_ids.append(file.id)

# gpt 갈구기
assistant = client.beta.assistants.create(
    name="SQL 질의문 작성자",
    instructions="당신은 전문적인 SQL 질의문 작성자입니다. 어떤한 정보에 대한 조회 요청이 들어오면, 해당하는 정보를 얻을 수 있는 SQL 질의문을 작성하여 응답합니다. 응답하기 전 파일들을 읽고 SQL 질의문 작성에 참조합니다. 테이블과 컬럼명은 반드시 전달된 문서에 작성된 이름을 수정 없이 그대로 사용합니다. 문서에 없는 컬럼과 테이블은 절대 사용하지 않습니다. 전달된 모든 파일을 반드시 읽습니다. 무조건 하나의 질의문으로 응답합니다.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {"file_ids": required_file_ids}
    }
)

thread = client.beta.threads.create(
    messages=[
        {
            "role": "assistant",
            # "content": '`liquibase-player.json` 파일은 "liquibase changeset" 파일이며, csv 파일이 아닌 json 형식의 파일입니다. 테이블들의 컬럼 중 primaryKey 속성을 가진 Id 이름의 컬럼은 User 테이블의 Id 컬럼 값을 무조건 사용하도록 DB에 입력되고 있습니다. 특정한 User의 정보를 알고 싶은 경우, 정보가 있을 것으로 생각되는 테이블의 Id 컬럼을 User 테이블의 Id 값으로 검색하면 됩니다. "수량" 으로는 `Amount` 컬럼을 사용하고, "지금까지 획득한 누적" 의미를 가진 컬럼은 `Acc` 접두사가 붙습니다. 첨부된 파일 중 *TableInfo.md 들은 접두사로 붙는 문자열이 테이블 명이며, 이는 liquibase-player.json 에 작성된 테이블들에 대한 설계 문서입니다. *TableInfo.md 파일은 하나가 아닌 여러 파일로 나눠져 있으므로, 모든 파일을 읽습니다. SQL 질의문 작성에 설계 문서를 참고하세요. 설계 문서 중 테이블 섹션의 표에서 "이름" 항목은 컬럼명을 의미합니다',
            "content": '테이블들의 컬럼 중 primaryKey (또는 PK 로 문서에 명시된) 속성을 가진 Id 이름의 컬럼은 User 테이블의 Id 컬럼 값을 무조건 사용하도록 DB에 입력되고 있습니다. 특정한 User의 정보를 알고 싶은 경우, 정보가 있을 것으로 생각되는 테이블의 Id 컬럼을 User 테이블의 Id 값으로 검색하면 됩니다. "수량" 으로는 `Amount` 컬럼을 사용하고, "지금까지 획득한 누적" 의미를 가진 컬럼은 `Acc` 접두사가 붙습니다. 첨부된 파일 중 *TableInfo.md 들은 접두사로 붙는 문자열이 테이블 명이며 작성된 테이블들에 대한 설계 문서입니다. *TableInfo.md 파일은 하나가 아닌 여러 파일로 나눠져 있으므로, 모든 파일을 읽습니다. SQL 질의문 작성에 설계 문서를 참고하세요. 설계 문서 중 테이블 섹션의 표에서 "이름" 항목은 컬럼명을 의미합니다',
        },
        {
            "role": "user",
            # "content": "닉네임이 우왕개멋짐인 유저의 100번 포인트 수량을 알고 싶어",
            "content": user_content,
        }
    ],
    tool_resources={
        "code_interpreter": {"file_ids": required_file_ids}
    }
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status != "completed":
    raise f"FAILED_GPT_REQUEST status({run.status}) last_error({run.last_error})"

# 갈군 결과
messages = client.beta.threads.messages.list(thread_id=thread.id)
result = messages.data[0].content[0].text.value
print(result)

# sql만 자름
sql_md_start_str = "```sql"
sql_md_end_str = "```"

start = result.find(sql_md_start_str)
if start < 0:
    raise "NOT_FOUND_SQL_IN_RESPONSE"
actual_start = start + len(sql_md_start_str) + 1 # 줄바꿈 하나까지 포함

end = result.find(sql_md_end_str, actual_start)

sql = result[actual_start:end]
sql = sql.replace("\n", " ")

# 진짜 결과
print(f'\nresult:"{sql}"')

