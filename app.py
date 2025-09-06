from flask import Flask, render_template, request
app = Flask(__name__)

class HammingCode:
    def __init__(self, message: str):
        self.message = message
        self.r = self._calculate_parity_bits(len(message))
        self.encoded = self._encode()

    def _calculate_parity_bits(self, m: int) -> int:
        r = 0
        while (2 ** r) < (m + r + 1):
            r += 1
        return r

    def _insert_parity_placeholders(self, data: str) -> str:
        j = 0
        k = 1
        m = len(data)
        res = ''
        for i in range(1, m + self.r + 1):
            if i == 2 ** j:
                res += '0'
                j += 1
            else:
                res += data[-k]
                k += 1
        return res[::-1]

    def _calculate_parity_values(self, arr: str) -> str:
        n = len(arr)
        arr = list(arr)
        for i in range(self.r):
            idx = 2 ** i
            parity = 0
            for j in range(1, n + 1):
                if j & idx:
                    parity ^= int(arr[-j])
            arr[-idx] = str(parity)
        return ''.join(arr)

    def _encode(self) -> str:
        with_placeholders = self._insert_parity_placeholders(self.message)
        return self._calculate_parity_values(with_placeholders)

    def introduce_error(self, position: int) -> str:
        corrupted = list(self.encoded)
        corrupted[position - 1] = '1' if corrupted[position - 1] == '0' else '0'
        return ''.join(corrupted)

    def detect_error(self, received: str) -> int:
        n = len(received)
        error_pos = 0
        for i in range(self.r):
            idx = 2 ** i
            parity = 0
            for j in range(1, n + 1):
                if j & idx:
                    parity ^= int(received[-j])
            if parity:
                error_pos += idx
        return error_pos

    def correct_error(self, received: str) -> str:
        error_pos = self.detect_error(received)
        if error_pos:
            corrected = list(received)
            corrected[error_pos - 1] = '1' if corrected[error_pos - 1] == '0' else '0'
            return ''.join(corrected), error_pos
        return received, 0

    def get_encoded(self) -> str:
        return self.encoded

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if request.method == 'POST':
        message = request.form['message']
        error_pos = int(request.form['error_pos']) if request.form['error_pos'] else 0

        hc = HammingCode(message)
        encoded = hc.get_encoded()
        corrupted = hc.introduce_error(error_pos) if error_pos else encoded
        corrected, detected_pos = hc.correct_error(corrupted)

        result = {
            'original': message,
            'encoded': encoded,
            'corrupted': corrupted,
            'corrected': corrected,
            'error_position': detected_pos
        }

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
