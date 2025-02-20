import streamlit as st

st.markdown("""
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    .team-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin-top: 20px;
    }
    .row {
        display: flex;
        justify-content: center; /* Center the cards horizontally */
        align-items: center;
        margin: 30px 0;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 30px;
        margin: 0 20px; /* Adjusted margin between cards */
        text-align: center;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        min-width: 350px; /* Increased min-width for wider cards */
        max-width: 400px; /* Increased max-width for wider cards */
    }
    .card i {
        font-size: 120px;
        color: #808080; /* Gray color */
        margin-bottom: 20px;
    }
    .card h3 {
        margin-bottom: 15px;
        font-size: 1.5em;
    }
    .card p {
        margin: 5px 0;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

st.header("Meet My Team")

st.markdown('<div class="team-container">', unsafe_allow_html=True)

def display_card(name, job, location, gender):
    icon = "fa-user"  
    if gender == "female":
        icon = "fa-user-circle"  
    elif gender == "male":
        icon = "fa-user" 

    st.markdown(f'''
        <div class="card">
            <i class="fas {icon}"></i>
            <h3>{name}</h3>
            <p>{job}</p>
            <p>{location}</p>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="row">', unsafe_allow_html=True)
display_card("Nicolen Evanz Aricayos", "Prompt Engineer", "Quezon City, Gateway Tower 2", "male")
display_card("Ronald Gulong", "Prompt Engineer", "Quezon City, Gateway Tower 2", "male")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="row">', unsafe_allow_html=True)
display_card("Sergio Vocales Jr.", "Data Engineer", "Quezon City, Gateway Tower 2", "male")
display_card("Junika Calupas", "Data Engineer", "Quezon City, Gateway Tower 2", "female")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="row">', unsafe_allow_html=True)
display_card("Charlene Reyes", "Frontend Developer", "Quezon City, Gateway Tower 2", "female")
display_card("Celine Andrea Perez", "Frontend Developer", "Quezon City, Gateway Tower 2", "female")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="row">', unsafe_allow_html=True)
display_card("Michelle Joy Barredo", "Tester", "Quezon City, Gateway Tower 2", "female")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
