import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import base64
from services.employee_service import fetch_employees, fetch_certifications



try:
       
        df_employees = fetch_employees()
        df_certifications =  fetch_certifications()

except Exception as e:
       st.error(f"Error fetching data: {e}")
       df_employees = pd.DataFrame()
       df_certifications = pd.DataFrame()

def people_lead_name(name):
        
        if not name:
                return 'Unknown'
        
        parts = name.split('.')

        name_format = ' '.join(part.capitalize() for part in parts)
        return name_format


def display_employee_profile(employee_data, profile_pic=None):
 
        
        st.markdown(
                f'''
                <div style="background-color: #8660D1; text-align: center; margin: 0px; border-radius: 10px;">
                 <h2>Profile Overview</h2>
                 <div style="margin-bottom: 30px;"></div>
                </div>
                ''',
                unsafe_allow_html=True
                  )

        if profile_pic:
               st.markdown(
            f'''
            <div style="text-align: center;">
                <div style="
                    display: inline-block;
                    width: 150px;
                    height: 150px;
                    border-radius: 50%;
                    overflow: hidden;
                    border: 2px solid #ddd;
                    ">
                    <img src="data:image/jpeg;base64,{profile_pic}" 
                         style="
                         width: 100%; 
                         height: 100%; 
                         object-fit: cover;"/>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
               
        st.markdown(
        f'''
        <div style="text-align: center; margin: 20px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0px; justify-content: center; text-align: left;">
                <div>
                    <p><strong>Name:</strong> {employee_data['first_name']} {employee_data['last_name']}</p>
                    <p><strong>EID:</strong> {employee_data['eid']}</p>
                    <p><strong>Current Project Name:</strong> {employee_data['project_name']}</p>
                </div>
                <div>
                    <p><strong>Capability:</strong> {employee_data['capability']}</p>       
                    <p><strong>Management Level:</strong> {employee_data['management_level']}</p>
                    <p><strong>People Lead:</strong> {people_lead_name(employee_data['manager_eid'])}</p>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def display_cerftications(certifications_df, eid):
      
            mycertifications = certifications_df[
                 (certifications_df['EID'] == eid) & (certifications_df['CURRENT_PROGRESS'] == 'Passed')][['TARGET_CERTIFICATION', 'EXPIRATION_DATE']]
            
            mycertifications = mycertifications.rename(columns={'TARGET_CERTIFICATION': 'Certification Name', 'EXPIRATION_DATE': 'Expiration Date'})
            
            
            mycertifications.reset_index(drop=True, inplace=True)
            mycertifications.index = mycertifications.index + 1

            if not mycertifications.empty:
                st.markdown(
                        '''
                        <div style="background-color: #3D9EF9; padding: 10px; border-radius: 10px;">
                        <h4 style="marrgin": 0;color:#ffffff >My Certifications</h4>
                        </div>
                        ''',
                        unsafe_allow_html=True
                )
                
                table_html = mycertifications.to_html(classes='styled-table', index=True)
        
        
                st.markdown(
                        f'''
                                <style>
                                .styled-table {{
                                width: 100%;
                                border-collapse: collapse;
                                border-radius: 10px;
                                overflow: hidden;
                                                 }}
                                .styled-table thead {{
                                background-color: #11B051;
                                color: #ffffff;
                                text-align: left;
                                        }}
                                .styled-table th, .styled-table td {{
                                padding: 12px; text-align: center;
                                border-bottom: 1px solid #ddd;
                                }}
                                .styled-table tbody tr:nth-child(even) {{
                                background-color: #f2f2f2;
                                }}
                                .styled-table tbody tr:hover {{
                                background-color: #E5E2E2;
                                }}
                                </style>
                                ''',
                        unsafe_allow_html=True
                )
                
                st.markdown(table_html, unsafe_allow_html=True)


                
                

            else:
                st.write("No certifications passed found for this employee.")        





if not df_employees.empty:

        first_employee = df_employees.iloc[0]
        first_employee_dict = first_employee.to_dict()

        user_data = {'first_name': first_employee_dict.get('FIRST_NAME'),
                'last_name': first_employee_dict.get('LAST_NAME'),
                'eid': first_employee_dict.get('EID'),
                'capability': first_employee_dict.get('CAPABILITY'),
                'management_level': first_employee_dict.get('MANAGEMENT_LEVEL'),
                'project_name': first_employee_dict.get('PROJECT_NAME'),
                'manager_eid': first_employee_dict.get('MANAGER_EID'),
                }
        

        if 'profile_pic_base64' not in st.session_state:
               st.session_state.profile_pic_base64 = None


        profile_pic = st.sidebar.file_uploader("Upload a Profile Picture", type=["jpg", "jpeg", "png"])
        if profile_pic:
            image = Image.open(profile_pic)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            st.session_state.profile_pic_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
       



        display_employee_profile(user_data, st.session_state.profile_pic_base64)

        if not df_certifications.empty:
               display_cerftications(df_certifications, user_data['eid'])
        else:
                st.write("No certification data available")

else:
       st.write("No employee data available")

