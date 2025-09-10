"""Prompt class for generating prompts"""

import json


class Prompts:
    """Class for generating prompts"""

    @staticmethod
    def get_tags_prompt(transcribed_and_diarized: str) -> tuple:
        """
        Generate a prompt for getting tags from OpenAI.

        Parameters
        ----------
        transcribed_and_diarized : str
            The transcribed and diarized conversation.

        Returns
        -------
        tuple
            A tuple containing the system message and user message.
        """
        system_message = "You are a helpful analysis of transactional sales data."
        user_message = f"Return a comma-separated list of maximum five tags for the following conversation. \n\n Conversation: {transcribed_and_diarized}"
        return system_message, user_message

    @staticmethod
    def summarize_conversation_prompt(transcribed_and_diarized: str) -> tuple:
        """
        Generate a prompt for summarizing a conversation.

        Parameters
        ----------
        transcribed_and_diarized : str
            The transcribed and diarized conversation.

        Returns
        -------
        tuple
            A tuple containing the system message and user message.
        """
        system_message = "You are a helpful assistant for summarizing conversations."
        # user_message = f"Summarize the following conversation in a concise manner. Clearly state the objectives for all speakers. \n\n Conversation: {transcribed_and_diarized}"

        user_message = f"""
        Conversation:
        {transcribed_and_diarized}
        Your task is to create a summary of the presented conversation. If possible, the summary should include:
            - The reason for the customer's contact with support.
            - A brief description of the resolution process and the outcome.
            - The company's products and any offers made by the operator to the customer.
            - A one-sentence evaluation of the customer's satisfaction.
            - If follow-up call necessary, then True, else False.
            - Tone of voice on the scale from 1 to 5 for these pairs, assigning 1 more close to the first pair and vice versa
                1. formal -> casual
                2. serious -> funny
                3. respectfully -> irreverent
                4. matter of fact -> enthusiastic
            - A comma-separated list of maximum five tags for the following conversation.

         Conversely, the summary should not include:
            - Personal information of the customer and operator (e.g., names, addresses).
            - Greetings exchanged between the customer and operator.

        Return result as simple JSON:
            {{
                "reason": "",
                "description": "",
                "products": [""],
                "satisfaction": "",
                "fup": "",
                "tone_of_voice": [
                    {{"formal_casual": ""}},
                    {{"serious_funny": ""}},
                    {{"respect_irreverent": ""}},
                    {{"mof_enthusiastic": ""}}
                ],
                "tags": [""]
            }}
        """  # noqa: E101, W191
        return system_message, user_message

    @staticmethod
    def get_sentiment_score_prompt(transcribed_and_diarized: str) -> tuple:
        """
        Generate a prompt for getting the sentiment score of a conversation.

        Parameters
        ----------
        transcribed_and_diarized : str
            The transcribed and diarized conversation.

        Returns
        -------
        tuple
            A tuple containing the system message and user message.
        """
        system_message = (
            "Provide a floating-point representation of the sentiment of "
            + "the following customer product review that is "
            + "rounded to five decimal places. "
            + "The scale ranges from -1.0 (negative) to 1.0 (positive) "
            + "where 0.0 represents neutral sentiment. "
            + "Only return the sentiment score value and nothing else. "
            + "You may only return a single numeric value."
        )
        user_message = f"Conversation: {transcribed_and_diarized}"
        return system_message, user_message

    @staticmethod
    def parse_summary_response(raw_response: str) -> dict:
        """
        Parse OpenAI's response, clean code block markers, and convert to JSON.

        Parameters
        ----------
        raw_response : str
            The raw response from OpenAI.

        Returns
        -------
        dict
            Parsed JSON dictionary.

        Raises
        ------
        ValueError
            If JSON decoding fails or required keys are missing.
        """
        lines = raw_response.splitlines()
        json_lines = [line for line in lines if not line.startswith("```")]
        json_str = "\n".join(json_lines)

        try:
            summary_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        # Validate required keys
        required_keys = [
            "reason",
            "description",
            "products",
            "satisfaction",
            "fup",
            "tone_of_voice",
            "tags",
        ]
        for key in required_keys:
            if key not in summary_dict:
                raise ValueError(f"Missing expected key in summary: '{key}'")

        return summary_dict
