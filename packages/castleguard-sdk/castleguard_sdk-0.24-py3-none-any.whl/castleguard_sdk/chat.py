

from datetime import datetime
import json

import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class ChatOptions:
    def __init__(
        self,
        best_of=None,
        echo=None,
        frequency_penalty=None,
        logit_bias=None,
        logprobs=None,
        max_tokens=None,
        n=None,
        presence_penalty=None,
        seed=None,
        stop=None,
        stream=None,
        stream_options=None,
        suffix=None,
        temperature=None,
        top_p=None,
        user=None,
        top_k=None,
        override_prompt=None,
        repetition_penalty=None,
        min_p=None,
        use_beam_search=None,
        length_penalty=None,
        early_stopping=None,
        stop_token_ids=None,
        ignore_eos=None,
        min_tokens=None,
        prompt_logprobs=None,
        detokenize=None,
        skip_special_tokens=None,
        spaces_between_special_tokens=None,
        logits_processors=None,
        truncate_prompt_tokens=None,
    ):
        self.best_of = best_of
        self.echo = echo
        self.frequency_penalty = frequency_penalty
        self.logit_bias = logit_bias
        self.logprobs = logprobs
        self.max_tokens = max_tokens
        self.n = n
        self.presence_penalty = presence_penalty
        self.seed = seed
        self.stop = stop
        self.stream = stream
        self.stream_options = stream_options
        self.suffix = suffix
        self.temperature = temperature
        self.top_p = top_p
        self.user = user
        self.top_k = top_k
        self.override_prompt = override_prompt
        self.repetition_penalty = repetition_penalty
        self.min_p = min_p
        self.use_beam_search = use_beam_search
        self.length_penalty = length_penalty
        self.early_stopping = early_stopping
        self.stop_token_ids = stop_token_ids
        self.ignore_eos = ignore_eos
        self.min_tokens = min_tokens
        self.prompt_logprobs = prompt_logprobs
        self.detokenize = detokenize
        self.skip_special_tokens = skip_special_tokens
        self.spaces_between_special_tokens = spaces_between_special_tokens
        self.logits_processors = logits_processors
        self.truncate_prompt_tokens = truncate_prompt_tokens


def snake_to_pascal(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_'))


class Chat(CastleGuardBase):

    def chat(self, prompt, chat_id=None, collection_id=None, expert_ids=None, model="default", store_in_db=True, chat_options=None):
        """
        Interacts with the chat endpoint to generate a response from the model.

        :param prompt: The input prompt to send to the model.
        :param chat_id: Optional chat session ID.
        :param collection_id : int | Iterable[int] | Sequence[int] | None, optional
        :param expert_ids: int | Iterable[int] | Sequence[int] | None, optional
        :return: Chatbot response or 'Unknown' if the request fails.
        """

        collection_id_list = self.normalize_to_list(collection_id, int)
        expert_id_list = self.normalize_to_list(expert_ids, int)
        print("collection_id_list", collection_id_list)
        if chat_id is None:
            chat_id = 0
        if chat_options is None:
            chat_options = ChatOptions()

        return self.send_message_to_chat(chat_id, prompt, collection_id_list, expert_id_list, model, store_in_db, **chat_options.__dict__)

    def chat_with_collection(self, prompt, collection_id=None, chat_id=None, chat_options=None):
        """
        Interacts with the chat endpoint to generate a response from the model.

        :param prompt: The input prompt to send to the model.
        :param chat_id: Optional chat session ID.
        :return: Chatbot response or 'Unknown' if the request fails.
        """

        # create a new chat session
        if chat_id is None:
            chat_id = self.create_chat()
        if chat_id is None:
            return "", None

        if chat_options is None:
            chat_options = ChatOptions()

        return self.send_message_to_chat(chat_id, prompt, [collection_id], [], "default", True, **chat_options.__dict__)

    def create_chat(self):

        url = self.get_url('chat-completion/chat')
        headers = self.get_headers()

        params = {
            "displayName": "Chat " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        chat_response = requests.post(url, headers=headers, params=params)
        if chat_response.status_code == 200:
            return json.loads(chat_response.text).get('id')
        else:
            self.log("Failed to create chat session", logLevel=3)
            self.log(f"Error: {chat_response.text} statuse{chat_response.status_code}", logLevel=3)
            return None

    def send_message_to_chat(self, chat_id, prompt, collection_ids=[], expert_ids=[], model="default", store_in_db=True, **kwargs):

        # Post a message to the chat
        message_url = f'{self.base_url}/chat-completion/completions/simple'

        payload = {
            "ChatId": 0 if not chat_id else chat_id,
            "Model": model if model is not None else "",
            "Prompt": prompt,
            "ExpertIds": expert_ids or [],
            "CollectionIds": collection_ids or [],
        }

        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue

            payload[snake_to_pascal(key)] = value

        try:
            headers = self.get_headers()
            headers["X-Persist-To-User-Store"] = str(store_in_db).lower()

            message_response = requests.post(message_url, json=payload, headers=headers)
            message_response.raise_for_status()  # Check for HTTP errors
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to get response for prompt: {prompt}", logLevel=3)
            self.log(f"Error: {e}", logLevel=3)
            return "Unknown", chat_id
        response_dict = json.loads(message_response.text)
        bot_message = response_dict.get('botMessage')
        chat_message = bot_message.get('chatMessage')
        return chat_message, chat_id
