
# UrbanMatch  API

## To Run the Application:

1. **Clone the Repository**

   Clone the repository to your local machine using the following command:
   ```bash
   git clone https://github.com/ashavijit/UrbanMatch-PythonTask.git
   ```

2. **Create a Virtual Environment**

   Create a virtual environment to manage dependencies:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**

   - **On Windows:**
     ```bash
     venv\Scripts\activate
     ```

   - **On macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install the Requirements**

   Install the required packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**

   Start the FastAPI application using `uvicorn`:
   ```bash
   uvicorn main:app --reload
   ```

6. **Open the Browser**

   Navigate to the following URL to see the home page:
   ```
   http://localhost:8000/
   ```

7. **Access the Documentation**

   To view the API documentation, go to:
   ```
   http://localhost:8000/docs
   ```

### API Endpoints Available:

- **`GET /`**
  - Returns the home page.

- **`POST /users/`**
  - Create a new user profile.
  - **Request Body:**
    ```json
    {
      "name": "Avijit Sen",
      "age": 22,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking", "reading"]
    }
    ```
  - **Response:**
    ```json
    {
      "id": 1,
      "name": "Avijit Sen",
      "age": 22,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking", "reading"]
    }
    ```

- **`GET /users/`**
  - Retrieve a list of user profiles.
  - **Query Parameters:**
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.
  - **Response:**
    ```json
    [
      {
        "id": 1,
        "name": "Avijit Sen",
        "age": 22,
        "gender": "Male",
        "email": "avijitsen.me@gmail.com",
        "city": "Kharagpur",
        "interests": ["traveling", "cooking", "reading"]
      }
    ]
    ```

- **`GET /users/{user_id}`**
  - Retrieve a user profile by ID.
  - **Path Parameters:**
    - `user_id`: The ID of the user.
  - **Response:**
    ```json
    {
      "id": 1,
      "name": "Avijit Sen",
      "age": 22,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking", "reading"]
    }
    ```

- **`PUT /users/{user_id}`**
  - Update a user profile by ID.
  - **Path Parameters:**
    - `user_id`: The ID of the user.
  - **Request Body:**
    ```json
    {
      "name": "Avijit Sen",
      "age": 23,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking"]
    }
    ```
  - **Response:**
    ```json
    {
      "id": 1,
      "name": "Avijit Sen",
      "age": 23,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking"]
    }
    ```

- **`DELETE /users/{user_id}`**
  - Delete a user profile by ID.
  - **Path Parameters:**
    - `user_id`: The ID of the user.
  - **Response:**
    ```json
    {
      "id": 1,
      "name": "Avijit Sen",
      "age": 23,
      "gender": "Male",
      "email": "avijitsen.me@gmail.com",
      "city": "Kharagpur",
      "interests": ["traveling", "cooking"]
    }
    ```

- **`GET /users/{user_id}/matches`**
  - Find potential matches for a user based on their interests.
  - **Path Parameters:**
    - `user_id`: The ID of the user.
  - **Response:**
    ```json
    [
      {
        "id": 2,
        "name": "John Doe",
        "age": 25,
        "gender": "Male",
        "email": "john.doe@example.com",
        "city": "Kolkata",
        "interests": ["traveling", "cooking"]
      }
    ]
    ```
