# AutoFaceCheckIn

AutoFaceCheckIn is an innovative attendance management system powered by facial recognition technology. It offers a seamless and efficient way to automate attendance tracking in various environments, including classrooms, workplaces, and events.

## Required Software

- Python 3
- MongoDB
- Git

## How to Run the App

To run AutoFaceCheckIn on your local machine, follow these steps:

1. **Clone the Repository**: Clone this repository to your local machine using Git:

```
git clone https://github.com/your_username/AutoFaceCheckIn.git
```

2. **Install Dependencies**: Navigate to the project directory and install the required dependencies using pip:

```
cd AutoFaceCheckIn
pip3 install -r requirements.txt

```

3. **Set Up MongoDB**: Install MongoDB on your machine if you haven't already. Then, start the MongoDB service.

4. **Run the App**: Start the Flask development server:

```
python3 run.py
```

5. **Access the App**: Open your web browser and go to `http://localhost:3000` to access the AutoFaceCheckIn web application.

## Available Pages and Functionality

- `/`: Home page of the AutoFaceCheckIn web application.
- `/login`: Login page for users to authenticate themselves.
- `/register`: Registration page for new users to create an account.
- `/capture`: Route for capturing images for facial recognition. Handles image capture and storage.
- `/imageData`: Route for retrieving and displaying user images stored in the database.
- `/user`: User dashboard page, where users can view their attendance records and manage their account settings.
