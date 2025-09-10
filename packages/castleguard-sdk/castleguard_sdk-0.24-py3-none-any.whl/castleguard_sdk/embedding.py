
import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Embedding(CastleGuardBase):

    def get_text_embedding(self, text):
        """
        Get an embedding vector for the given text.

        :param text: The input text for which the embedding will be created.
        :return: A list of floats representing the text embedding.
        """
        url = f'{self.base_url}/embedding/from-chunk'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = { "chunkText": text }
        
        result = None
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                self.log(f"Failed to retrieve embedding vector: {response.text}", logLevel=3)
                return None
            
            json_value = response.json()
            if json_value is not None:
                return json_value
        except requests.RequestException as e:
            self.log(f"get_text_embedding request failed: {e}", logLevel=3)
            return None
            
        return result
