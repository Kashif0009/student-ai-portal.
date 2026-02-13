🎓 EduPredict Pro: AI-Driven Student Diagnostic Portal
EduPredict Pro is a full-stack AI application designed to help educators identify at-risk students and simulate academic interventions. By combining predictive modeling with a "What-If" simulator, this tool provides actionable insights rather than just static data.

🚀 Key Features
Hybrid ML Engine: Uses a Random Forest architecture to perform both Grade Prediction (Regression) and Risk Classification (Categorization).

Prescriptive "What-If" Simulator: A digital twin tool that allows teachers to simulate habit changes (e.g., increasing study hours) to see real-time impact on predicted grades.

Secure Infrastructure: Integrated SQLite3 database for user registration and historical record persistence.

Advanced Analytics: Interactive Radar Charts for behavioral balance analysis (Sleep vs. Study vs. Social media).

Data Security: Implementation of the latest PBKDF2 hashing for secure password storage via streamlit-authenticator.

🛠️ Tech Stack
📂 Project Structure
⚙️ Local Setup Instructions
Clone the Repository:

Install Dependencies:

Run the App:

🧠 Model Logic
The model interprets the "Student Lifecycle" by evaluating variables like:

Habit Ratio: The efficiency of study hours vs. digital distractions.

Consistency: Attendance percentages mapped against missed deadlines.

Social Context: Parental education levels and demographic data.

The system uses Feature Scaling to ensure that variables like "Attendance (0-100)" do not outweigh "Study Hours (0-15)" during the decision-tree process.



<img width="1360" height="595" alt="s1" src="https://github.com/user-attachments/assets/6b398e3d-812b-4b27-bb91-59abdfe4692b" />
<img width="1360" height="619" alt="s2" src="https://github.com/user-attachments/assets/c228bf36-15fb-41c2-8de2-f6e8b0bd1575" />
<img width="1364" height="617" alt="s3" src="https://github.com/user-attachments/assets/04f37601-bd9e-4ecb-a8a6-d3e37cc59d4c" />
<img width="1358" height="611" alt="s4" src="https://github.com/user-attachments/assets/aef68b4f-4b28-4e3f-9cd2-df70f6404692" />
<img width="1358" height="608" alt="s5" src="https://github.com/user-attachments/assets/3111c8f4-00ee-4e5d-83a2-8e3e117fcce9" />


