from .ApiOpenAi import ApiOpenAi

import templates
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA


class ApiChatGpt(ApiOpenAi):
    def __init__(self, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.provider_name = "ChatGPT"
        self.dry_run_object = templates.dry_run_story
        self.recyclable_item = ""
        self.temperature = 0.9
        self.as_string = True

    def fetch_prompt(
        self, item="metal can", prompt_template="pollution_prompt_template", **kwargs
    ):
        llm = OpenAI(
            model_name="gpt-4",
            temperature=self.temperature,
            openai_api_key=self.api_key,
        )

        # prompt = PromptTemplate(
        #     input_variables=["item"],
        #     template=eval(prompt_template),
        # )

        if not self.dry_run:
            prompt = eval(prompt_template) + f" {item}"
            story = llm(prompt)
            if self.as_string:
                return story

            filename = f"{item}_{story[:20].replace(' ','')}"
            if len(filename) > 250:
                filename = filename[:250]

            story_folder = "pollution_scenes"
            with open(f"{story_folder}/{filename}.txt", "w") as file:
                # Write the string to the file
                file.write(story)

            print(f"pollution prompt saved at {story_folder}/{filename}.txt")
            return story

        else:
            return eval("dry_run_" + prompt_template)

    def fetch_using_index(self, query="in 1990, how much paper was generated?"):
        """
        call self.produce_index_pinecone(self,index_name='cfc',docs_dir="recycling_data_dir",embeddings=None) first
        """
        if not self.dry_run:
            self.produce_index_pinecone(index_name="cfc", docs_dir="recycling_data")

            qa = RetrievalQA.from_chain_type(
                llm=OpenAI(temperature=0.5),
                chain_type="stuff",
                return_source_documents=True,
                retriever=self.index.as_retriever(
                    search_type="mmr", search_kwargs={"k": 1}
                ),
            )
            # qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.5), chain_type="stuff", return_source_documents=True ,retriever=self.index.as_retriever(search_kwargs={"k":4}))
            # qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.5), chain_type="stuff",retriever=self.index.as_retriever(search_kwargs={"k":4}))

            response = qa({"query": query}, return_only_outputs=True)
            result = response["result"]
            source = response["source_documents"][0].metadata["source"]

            return {"result": result, "source": source}

        else:
            return templates.dry_run_index_fetch

    def fetch_story(
        self,
        recyclable_item=False,
        story_setting=False,
        obstacle=False,
        temperature=0.9,
        as_string=True,
        dry_run=False,
        nber_pages=5,
    ):
        """
        temp is a float 0.01 to 1.0  The higher the number the more creative the answer
        """
        llm = OpenAI(
            model_name="gpt-4", temperature=temperature, openai_api_key=self.api_key
        )

        prompt = PromptTemplate(
            input_variables=["item", "setting", "obstacle", "nber_pages"],
            template=templates.base_template + templates.variable_template,
        )

        if not self.dry_run and not dry_run:
            story = llm(
                prompt.format(
                    item=recyclable_item,
                    setting=story_setting,
                    obstacle=obstacle,
                    nber_pages=nber_pages,
                )
            )
            if as_string:
                return story

            filename = f"{recyclable_item}_{story_setting}_{obstacle}"
            if len(filename) > 250:
                filename = filename[:250]

            story_folder = "stories"
            with open(f"{story_folder}/{filename}.txt", "w") as file:
                # Write the string to the file
                file.write(story)

            return f"{story_folder}/{filename}.txt"

        else:
            # print(f"would have created a story with {self.provider_name} using prompt {prompt}")
            return templates.dry_run_story

    def fetch_img_prompts(self, story, nber_pages):
        llm = OpenAI(model_name="gpt-4", temperature=0.1, openai_api_key=self.api_key)

        if not self.dry_run:
            instructions = (
                templates.prompt_descriptive_dictionary.format(nber_pages=nber_pages)
                + templates.example_json_output
                + f" here is the story: {story}"
            )
            story_descriptive_dictionary = llm(instructions)
            story_descriptive_dictionary = eval(story_descriptive_dictionary)
            pages = story_descriptive_dictionary["story_pages"]
            new_pages = []
            for idx, page in enumerate(pages):
                for character in story_descriptive_dictionary["characters"].keys():
                    page["image_prompt"] = page["image_prompt"].replace(
                        character, story_descriptive_dictionary["characters"][character]
                    )
                    page["image_prompt"] += f" do not show {self.recyclable_item}"
                new_pages.append(page)
            # #img_prompts=[page['image_prompt'].replace(character,pages['characters'][character]) for page in pages for character in pages['characters'].keys()]
            # page_texts=[page['text'] for page in pages]
            story_descriptive_dictionary["story_pages"] = new_pages
            return story_descriptive_dictionary
        return {}

    def fetch_sfx_prompts(self, story):
        llm = OpenAI(model_name="gpt-4", openai_api_key=self.api_key)

        prompt = PromptTemplate(input_variables=["story"], template=templates.sfx_prompt_template)

        if not self.dry_run:
            sfx_prompt = llm(prompt.format(story=story))
            return sfx_prompt
        return None
