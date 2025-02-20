import streamlit as st
 
 
# Title and Introduction
st.title("Help Center")
st.markdown("""
Welcome to your ultimate guide for managing and tracking certifications! Navigate through the sections below to get detailed information on how to use our features and get support when you need it.
""")
 
# Sidebar for navigation
st.sidebar.title("Quick Navigation")
st.sidebar.markdown("""
- [🛠️ Getting Started](#getting-started)
- [🔧 How to Use](#how-to-use)
- [❓ FAQ](#faq)
- [🗨️ Support Center](#support-center)
- [⚙️ Troubleshooting](#troubleshooting)
- [📚 User Guide](#user-guide)
- [📞 Contact Support](#contact-support)
- [🔗 Help Resources](#help-resources)
""")
 
# Frame for content with expandable sections
with st.container():
    st.markdown('<a id="getting-started"></a>', unsafe_allow_html=True)
    st.subheader("🛠️ Getting Started")
    with st.expander("Expand for Details", expanded=True):
        st.markdown("""
        **Welcome aboard!** 🚀
        \n**Here’s how to kick off your certification tracking journey:**\n
                   
        - **Log In**: Access your dashboard with your credentials. """)
 
    st.markdown('<a id="how-to-use"></a>', unsafe_allow_html=True)
    st.subheader("🔧 How to Use")
    with st.expander("Expand for Details"):
        st.markdown("""
        Discover how to use the Certification Tracker like a pro:
 
        - **Dashboard Overview**: Use the dashboard to manage certifications and deadlines.
        - **Add Certifications**: Click 'Add Certification' to input details and track your progress.
        - **Monitor Progress**: Keep track of your achievements and upcoming deadlines.
 
        """)
 
    st.markdown('<a id="user-guide"></a>', unsafe_allow_html=True)
    st.subheader("📚 User Guide")
    with st.expander("Expand for Details"):
        st.markdown("""
        Dive into our comprehensive User Guide to maximize your use of the tracker:
 
        - **Feature Overview**: Learn about the full range of features.
        - **Step-by-Step Instructions**: Follow detailed steps for all functionalities.
                   
        """)
 
    st.markdown('<a id="faq"></a>', unsafe_allow_html=True)
    st.subheader("❓ FAQ")
    with st.expander("Expand for Details"):
        st.markdown("""
        **Got Questions?** Here are some common answers:
 
        - **Can I track multiple certifications?**  
        Yes, you can categorize and track certifications from various fields.
 
        - **What if I encounter a technical issue?**  
        Refer to our 'Troubleshooting' section or contact support.
 
        Explore more in our [Support Center](#support-center).
        """)
 
    st.markdown('<a id="support-center"></a>', unsafe_allow_html=True)
    st.subheader("🗨️ Support Center")
    with st.expander("Expand for Details"):
        st.markdown("""
        Need additional support? Here’s how you can get it:
 
        - **Community Forum**: Join discussions with other users.
        - **Submit a Ticket**: For direct help, submit a ticket and our team will assist you.
 
        """)
 
    st.markdown('<a id="contact-support"></a>', unsafe_allow_html=True)
    st.subheader("📞 Contact Support")
    with st.expander("Expand for Details"):
        st.markdown("""
        We’re here to assist you:
 
        - **Email Support**: Contact us at support@example.com.
        - **Phone Support**: Call us at (02)8532-1234.
                   
        We’re ready to help with any questions or issues!
        """)
 
    st.markdown('<a id="help-resources"></a>', unsafe_allow_html=True)
    st.subheader("🔗 Help Resources")
    with st.expander("Expand for Details"):
        st.markdown("""
        Enhance your experience with these resources:
 
        - **Tutorial Videos**: Watch [tutorials and demos](#) on our YouTube Channel.
        - **Blog**: Read the latest tips and updates on our [Blog](#).
 
        Check out these resources to get the most out of your Certification Tracker!
        """)
 
# Footer
st.markdown("""
Need further assistance or have other questions? Feel free to reach out to our support team. We're here to help you every step of the way!
""")
 