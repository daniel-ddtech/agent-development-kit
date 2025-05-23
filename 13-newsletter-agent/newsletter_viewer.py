import os
import streamlit as st
import glob
import markdown
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="AI & Gaming Newsletter Viewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMarkdown h1 {
        color: #1E88E5;
    }
    .stMarkdown h2 {
        color: #7E57C2;
        margin-top: 1.5rem;
    }
    .stMarkdown h3 {
        color: #43A047;
    }
    .rating-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .article-box {
        background-color: #f9f9f9;
        border-left: 3px solid #1E88E5;
        padding: 10px;
        margin-bottom: 10px;
    }
    .star-filled {
        color: #FFD700;
    }
    .star-empty {
        color: #CCCCCC;
    }
</style>
""", unsafe_allow_html=True)

def get_newsletter_files():
    """Get all newsletter markdown files in the directory"""
    return sorted(glob.glob("newsletter_*.md"), reverse=True)

def display_newsletter(file_path):
    """Display a newsletter with proper formatting"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract file creation date
        file_stat = os.stat(file_path)
        creation_date = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Display file info
        st.sidebar.info(f"File: {os.path.basename(file_path)}\nCreated: {creation_date}")
        
        # Convert markdown to HTML for better display
        html_content = markdown.markdown(content)
        
        # Replace star ratings with colored stars
        html_content = html_content.replace("★", "<span class='star-filled'>★</span>")
        html_content = html_content.replace("☆", "<span class='star-empty'>☆</span>")
        
        # Display the content
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Add download button
        st.download_button(
            label="Download Newsletter",
            data=content,
            file_name=os.path.basename(file_path),
            mime="text/markdown",
        )
        
    except Exception as e:
        st.error(f"Error displaying newsletter: {str(e)}")

def main():
    st.title("AI & Gaming Newsletter Viewer 🤖🎮")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Get all newsletter files
    newsletter_files = get_newsletter_files()
    
    if not newsletter_files:
        st.warning("No newsletter files found. Please run the newsletter generator first.")
        return
    
    # Create a dropdown to select newsletters
    selected_file = st.sidebar.selectbox(
        "Select Newsletter:",
        newsletter_files,
        format_func=lambda x: f"{os.path.basename(x)} ({os.path.getsize(x) / 1024:.1f} KB)"
    )
    
    # Generate button
    if st.sidebar.button("Generate New Newsletter"):
        with st.spinner("Generating newsletter..."):
            # Run the newsletter generator script
            os.system("python rated_newsletter_test.py")
            st.success("Newsletter generated! Refresh the page to see it.")
            st.experimental_rerun()
    
    # Display the selected newsletter
    if selected_file:
        display_newsletter(selected_file)
    
    # Sidebar additional info
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This viewer displays AI & Gaming newsletters generated by the newsletter system. "
        "Use the dropdown to select different newsletters, or generate a new one."
    )

if __name__ == "__main__":
    main()
