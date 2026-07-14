import string

class URLShortener:

    def __init__(self):
        # 62 characters for Base62: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.characters = string.digits + string.ascii_letters
        self.base = len(self.characters)  # 62

        # Dictionary to store { short_id: original_url }
        self.url_map = {}

        # Auto-incrementing counter for unique short IDs
        self.counter = 1000  # Starting at 1000 so IDs are at least 2 characters long
        
    def encode(self,num):
        """Encodes a number into a Base62 string."""
        if num == 0:
            return self.characters[0]
        
        encoded = []
        while num > 0:
            remainder = num % self.base
            encoded.append(self.characters[remainder])
            num //= self.base
        
        # Since we build the string in reverse order, we need to reverse it before returning
        return ''.join(reversed(encoded))

    def shorten(self, long_url):
        """Accepts a long URL, creates a unique Base62 short ID, and stores it."""
        short_id = self.encode(self.counter)
        self.url_map[short_id] = long_url
        self.counter += 1
        return short_id

    def get_url(self, short_id):
        """Retrieves the original URL for a given short ID, or returns None."""
        return self.url_map.get(short_id)