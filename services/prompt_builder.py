
class PromptBuilder:
    
    def build_prompt(self, query, chunks):
        """
            Builds the user prompt using the chunks with the highest scores by the reranker.
            Provides the chunk text as context and gives additional metadata for each chunk text,
            such as the page number, section title and document name from where the information was found.

        """
        system_prompt = (
                    "You are an AI assistant, answer the user's query using the context provided below. "
                    "Also provide information such as document name, page number where the answer was found and if given, mention the section title as well. "
                    "Provide an answer that is short and to the point. "
                    "If the answer cannot be found in the context provided then let the user know in the response.\n\n"
                )
        user_prompt = "Context:\n\n"
        for index, chunk in enumerate(chunks):
            if chunk['section_title']:
                user_prompt += (
                            f"Document {index+1}\n"
                            f"Document Name: {chunk['document_name']}\n"
                            f"Page Numbers:{chunk['page_numbers']}\n"
                            f"Section Title:{chunk['section_title']}\n"
                            f"Text: {chunk['text']}\n"
                            f"{'-'*60}\n\n"
                        )
            else:
                user_prompt += (
                            f"Document {index+1}\n"
                            f"Document Name: {chunk['document_name']}\n"
                            f"Page Numbers:{chunk['page_numbers']}\n"
                            f"Text: {chunk['text']}\n"
                            f"{'-'*60}\n\n"
                        )
        user_prompt += (f"Question:\n\n{query}")
        return system_prompt, user_prompt