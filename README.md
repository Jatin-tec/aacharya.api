# Aacharya

## Description

This is the backend for the Aacharya application. It is built using Flask, a lightweight web framework for Python.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Jatin-tec/aacharya.api.git
    ```

2. Navigate to the project directory:

    ```bash
    cd aacharya.api
    ```

3. Create a virtual environment:

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

5. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the Flask development server:

    ```bash
    flask run --debug
    ```

2. Open your web browser and navigate to `http://localhost:5000` to access the backend API.

## API Endpoints

- `/api/users`: Returns a list of all users.
- `/api/users/{id}`: Returns the details of a specific user.
- `/api/posts`: Returns a list of all posts.
- `/api/posts/{id}`: Returns the details of a specific post.

## Contributing

Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.