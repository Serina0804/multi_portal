from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from openai import AzureOpenAI
import json

# TeamC
api_base = "XXX"  # Your endpointgitsh
api_version = "XXX"  # API version to use
api_key = "XXX"  # Your API key

deployment_name = "gpt-4o-mini"  # Deployment name
model_name = "gpt-4o-mini"  # Model name

# Initialize the OpenAI client with Azure details
client = AzureOpenAI(
  api_key=api_key,  
  api_version="XXX",
  azure_endpoint=api_base
)


# Base model for output
class CodeGenResult(BaseModel):
    category: str = Field(description="カテゴリー分類の結果")
    sentiment: str = Field(description="感情分類の結果")

# Create JSON parser
parser = JsonOutputParser(pydantic_object=CodeGenResult)

# Prompt template
prompt_template = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "与えられた文章をカテゴリーと感情に分類してください。\n{format_instructions}\n"
        ),
        HumanMessagePromptTemplate.from_template("{query}"),
    ],
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Output instructions
print("===== format_instructions")
print(parser.get_format_instructions())
prompt_list = ["営業職に関する文章を書きたいです。"]
def main():
    while True:
        # input_text = input("文章を入力してください：")
        input_text = client.chat.completions.create(
            model=model_name,
            messages=[
            {
                            "role": "system",
                            "content": (
                                "様々な分野の文章を営業職に関するで文章を書くことができます。"
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"営業職の文章を書きたいです。：{prompt_list[-1]}"
                        }
                    ],
                    max_tokens=150,
                    n=1,
                    stop=None,
                    temperature=0.8,
        )
        # Provide instructions to the prompt
        prompt = prompt_template.format_prompt(query=input_text)
        prompt_list.append(input_text)
        print("===== プロンプト")
        print(prompt)

        # Convert the prompt to the correct format for OpenAI API

        # Execute the query using OpenAI API
        response = client.chat.completions.create(
            model=model_name,
            messages=[
            {
                            "role": "system",
                            "content": (
                                "あなたはユーザーフィードバックを事前に定義されたカテゴリに分類し、各カテゴリに対して感情分析を行うAIアシスタントです。"
                                "あなたの目標は、各フィードバックを分析し、最も関連性の高いカテゴリを割り当て、そのフィードバック内容に基づいてカテゴリごとの感情（ポジティブ、ネガティブ、ニュートラル）を判断することです。"
                                "カテゴリーは複数選ぶことができます。ただし、感情は1つだけ選択してください。"   
                                "事前定義されたカテゴリは次のとおりです：Q&A、商談方法、商談相手の性質、市場トレンド、商談の成功事例、商談の失敗事例、市場動向、商材レビュー、日報、営業戦略、競合分析。"
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"入力する文章をカテゴリーと感情に分類してください：{prompt}"
                        }
                    ],
                    max_tokens=150,
                    n=1,
                    stop=None,
                    temperature=0.1,
        )
        print("===== モデルからの回答")
        print(response)

        # Correctly access the response
        response_content = response.choices[0].message.content

        # Parse the response
        result = parser.parse(response_content)
        print("===== Jsonパーサー適用後の回答")
        print(result)
        print("===== カテゴリー")
        print(result.get("category"))
        print("===== 感情")
        print(result.get("sentiment"))

if __name__ == "__main__":
    main()