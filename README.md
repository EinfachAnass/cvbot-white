

This project uses PyTorch, OpenCV, and Cvbot.. for object detection (in our case detecting a football)

# Environment Setup

# Option 1: Using Conda 

1. Create the environment:

   conda env create -f environment.yml

2. Activate the environment:

   conda activate catandball

# Option 2: Manual Setup (if option 1 didnt work)

If conda environment creation fails, you can set up manually:

1. Create a new conda environment:

   conda create -n catandball python=3.12

   then 

   conda activate catandball
   

2. Install conda packages:
   
   conda install -c conda-forge -c pytorch pytorch torchvision torchaudio opencv numpy pillow matplotlib pandas scipy


3. Install pip packages:
   
   pip install -r requirements.txt

