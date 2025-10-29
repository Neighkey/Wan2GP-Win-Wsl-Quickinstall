#!/bin/bash

################################################################################
# WGP Manager - All-in-One Management Script
################################################################################
# This script provides:
#   - Fresh WGP installation with Sage Attention
#   - Git repository updates
#   - Python dependency management
#   - CUDA toolkit installation
#   - Drive finding utilities
#   - WGP launcher
################################################################################

set -e  # Exit on error (disabled in menu mode)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default WGP installation directory
WGP_DIR="/mnt/d/wgp"
VENV_DIR="$WGP_DIR/venv"

# Print functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if WGP directory exists
check_wgp_dir() {
    if [ ! -d "$WGP_DIR" ]; then
        print_error "WGP directory not found at $WGP_DIR"
        echo "Please install WGP first or update WGP_DIR in this script."
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
}

# Run WGP
run_wgp() {
    print_header "Running WGP"
    cd "$WGP_DIR" || exit 1
    activate_venv
    python wgp.py
}

# Update Git repository
update_git() {
    print_header "Updating Git Repository"
    cd "$WGP_DIR" || exit 1
    
    print_info "Current branch:"
    git branch --show-current
    
    print_info "Fetching latest changes..."
    git fetch --all
    
    echo ""
    echo "Available remotes:"
    git remote -v
    
    echo ""
    echo "Which remote do you want to pull from?"
    echo "1) origin (current remote)"
    echo "2) upstream (if configured)"
    echo "3) deepbeep (original repo)"
    echo "4) Cancel"
    read -p "Enter choice [1-4]: " git_choice
    
    case $git_choice in
        1)
            print_info "Pulling from origin..."
            git pull origin $(git branch --show-current)
            print_success "Git repository updated from origin"
            ;;
        2)
            print_info "Pulling from upstream..."
            git pull upstream $(git branch --show-current)
            print_success "Git repository updated from upstream"
            ;;
        3)
            # Check if deepbeep remote exists
            if ! git remote | grep -q "deepbeep"; then
                print_info "Adding deepbeep remote..."
                git remote add deepbeep https://github.com/deepbeepmeep/Wan2GP.git
                git fetch deepbeep
            fi
            print_info "Pulling from deepbeep..."
            git pull deepbeep main
            print_success "Git repository updated from deepbeep"
            ;;
        4)
            print_info "Cancelled"
            ;;
        *)
            print_error "Invalid choice"
            ;;
    esac
}

# Update Python dependencies
update_python() {
    print_header "Updating Python Dependencies"
    cd "$WGP_DIR" || exit 1
    activate_venv
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing/updating requirements..."
    pip install -r requirements.txt --upgrade
    
    print_success "Python dependencies updated"
}

# Update both Git and Python
update_all() {
    update_git
    echo ""
    update_python
    print_success "All updates completed"
}

# Check status
check_status() {
    print_header "WGP Status"
    cd "$WGP_DIR" || exit 1
    
    echo -e "${YELLOW}Git Status:${NC}"
    git status
    
    echo ""
    echo -e "${YELLOW}Current Branch:${NC}"
    git branch --show-current
    
    echo ""
    echo -e "${YELLOW}Remotes:${NC}"
    git remote -v
    
    echo ""
    echo -e "${YELLOW}Python Version:${NC}"
    activate_venv
    python --version
    
    echo ""
    echo -e "${YELLOW}PyTorch Version:${NC}"
    python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')" 2>/dev/null || echo "PyTorch not installed"
    
    echo ""
    echo -e "${YELLOW}Disk Usage:${NC}"
    du -sh "$WGP_DIR"
}

# Open WGP directory
open_directory() {
    print_header "Opening WGP Directory"
    cd "$WGP_DIR" || exit 1
    print_success "Changed to $WGP_DIR"
    activate_venv
    exec bash
}

# Find available drives
find_drives() {
    print_header "Finding Available Drives in WSL"

    echo "Mounted drives in /mnt/:"
    ls -la /mnt/
    echo ""

    echo "Disk space information:"
    df -h | grep -E "Filesystem|/mnt/"
    echo ""

    echo "Common drive locations in WSL:"
    echo "  C: drive -> /mnt/c"
    echo "  D: drive -> /mnt/d"
    echo "  E: drive -> /mnt/e"
    echo "  F: drive -> /mnt/f"
    echo ""
}

# Install CUDA Toolkit
install_cuda() {
    print_header "Installing CUDA Toolkit 12.8"

    print_warning "This will install CUDA 12.8 toolkit (large download ~3GB)"
    read -p "Continue? (y/n): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Cancelled"
        return
    fi

    print_info "Checking for existing CUDA installation..."
    if command_exists nvcc; then
        NVCC_VERSION=$(nvcc --version | grep "release" || echo "Unknown")
        print_warning "CUDA already installed: $NVCC_VERSION"
        read -p "Reinstall anyway? (y/n): " reinstall
        if [ "$reinstall" != "y" ] && [ "$reinstall" != "Y" ]; then
            print_info "Cancelled"
            return
        fi
    fi

    # Download and install CUDA keyring
    print_info "Downloading CUDA keyring..."
    cd /tmp
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb 2>/dev/null || {
        print_warning "Download failed, trying without quiet mode..."
        wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
    }
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt-get update

    # Install CUDA toolkit 12.8
    print_info "Installing CUDA toolkit 12.8 (this takes 10-15 minutes)..."
    print_warning "Please be patient, this is a large download..."
    sudo apt-get install -y cuda-toolkit-12-8 || {
        print_warning "CUDA 12.8 installation failed, trying nvidia-cuda-toolkit from Ubuntu repo..."
        sudo apt install -y nvidia-cuda-toolkit
    }

    # Set CUDA environment variables
    print_info "Setting CUDA environment variables..."
    export CUDA_HOME=/usr/local/cuda
    export PATH=$CUDA_HOME/bin:$PATH
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

    # Add to bashrc if not already there
    if ! grep -q "CUDA_HOME" ~/.bashrc 2>/dev/null; then
        echo '' >> ~/.bashrc
        echo '# CUDA 12.8 Environment Variables' >> ~/.bashrc
        echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.bashrc
        echo 'export PATH=$CUDA_HOME/bin:$PATH' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        print_success "CUDA environment variables added to ~/.bashrc"
    fi

    # Verify installation
    if command_exists nvcc; then
        NVCC_VERSION=$(nvcc --version | grep "release" || echo "Unknown")
        print_success "CUDA installed successfully! $NVCC_VERSION"
    else
        print_warning "nvcc not found in PATH, trying to locate it..."

        # Try to find nvcc in common locations
        if [ -f /usr/bin/nvcc ]; then
            export CUDA_HOME=/usr
            export PATH=/usr/bin:$PATH
            print_success "Found nvcc at /usr/bin/nvcc"
        elif [ -f /usr/local/cuda/bin/nvcc ]; then
            export CUDA_HOME=/usr/local/cuda
            export PATH=/usr/local/cuda/bin:$PATH
            print_success "Found nvcc at /usr/local/cuda/bin/nvcc"
        elif [ -f /usr/local/cuda-12.8/bin/nvcc ]; then
            export CUDA_HOME=/usr/local/cuda-12.8
            export PATH=/usr/local/cuda-12.8/bin:$PATH
            print_success "Found nvcc at /usr/local/cuda-12.8/bin/nvcc"
        else
            print_error "Could not find nvcc anywhere!"
            print_info "You may need to restart your terminal or run: source ~/.bashrc"
        fi
    fi

    cd - > /dev/null
}

# Reinstall Sage Attention
reinstall_sage() {
    print_header "Installing/Reinstalling Sage Attention"

    if [ ! -d "$WGP_DIR" ]; then
        print_error "WGP not installed at $WGP_DIR"
        print_info "Please install WGP first (option 9)"
        return
    fi

    cd "$WGP_DIR" || exit 1
    activate_venv

    print_info "This will compile Sage Attention from source (15-30 minutes)..."
    read -p "Continue? (y/n): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Cancelled"
        return
    fi

    # Check if SageAttention directory exists
    if [ ! -d "SageAttention" ]; then
        print_info "Cloning Sage Attention repository..."
        git clone https://github.com/thu-ml/SageAttention.git
    fi

    cd SageAttention || exit 1

    # Set parallel compilation flags
    export EXT_PARALLEL=4
    export NVCC_APPEND_FLAGS="--threads 8"
    export MAX_JOBS=32

    # Set CUDA environment
    export CUDA_HOME=/usr/local/cuda
    export PATH=$CUDA_HOME/bin:$PATH
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

    print_info "Attempting to compile Sage Attention from source..."
    if python setup.py install 2>&1 | tee /tmp/sageattention_install.log; then
        print_success "Sage Attention compiled and installed successfully!"
    else
        print_error "Sage Attention compilation failed!"
        print_warning "Trying to install pre-built wheel instead..."

        if pip install sageattention; then
            print_success "Sage Attention installed from pre-built wheel!"
        else
            print_error "Pre-built wheel installation also failed!"
            print_info "Check /tmp/sageattention_install.log for details"
        fi
    fi

    cd "$WGP_DIR"
}

# Fresh WGP Installation
fresh_install() {
    print_header "Fresh WGP Installation with Sage Attention"

    echo "This will install:"
    echo "  - WGP (Video Editor branch)"
    echo "  - Sage Attention"
    echo "  - PyTorch with CUDA 12.8"
    echo "  - All dependencies"
    echo ""

    # Show available drives first
    print_info "Available drives and disk space:"
    echo ""
    df -h | grep -E "Filesystem|/mnt/" | grep -v "tmpfs"
    echo ""

    # Show common installation locations
    echo "Common installation locations:"
    echo "  1) /mnt/d/wgp (D: drive - recommended for second SSD)"
    echo "  2) /mnt/c/wgp (C: drive)"
    echo "  3) ~/wgp (Linux filesystem - fastest but uses WSL space)"
    echo "  4) Custom path"
    echo ""

    read -p "Choose location [1-4]: " location_choice

    case $location_choice in
        1)
            INSTALL_DIR="/mnt/d/wgp"
            ;;
        2)
            INSTALL_DIR="/mnt/c/wgp"
            ;;
        3)
            INSTALL_DIR="$HOME/wgp"
            ;;
        4)
            read -p "Enter custom installation path: " INSTALL_DIR
            ;;
        *)
            print_error "Invalid choice"
            return
            ;;
    esac

    echo ""
    echo "Installation directory: $INSTALL_DIR"
    echo ""

    # Show disk space at chosen location
    PARENT_DIR=$(dirname "$INSTALL_DIR")
    if [ -d "$PARENT_DIR" ]; then
        print_info "Available space at this location:"
        df -h "$PARENT_DIR" | tail -1
        echo ""
    fi

    read -p "Continue with this location? (y/n): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Cancelled"
        return
    fi

    # Check for Python
    print_info "Checking for Python installation..."
    PYTHON_CMD=""
    if command_exists python3.12; then
        PYTHON_CMD="python3.12"
    elif command_exists python3.11; then
        PYTHON_CMD="python3.11"
    elif command_exists python3.10; then
        PYTHON_CMD="python3.10"
    elif command_exists python3; then
        PYTHON_CMD="python3"
    else
        print_error "No Python found! Installing Python 3.10..."
        sudo apt update
        sudo apt install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install -y python3.10 python3.10-venv python3.10-dev
        PYTHON_CMD="python3.10"
    fi
    print_success "Using $PYTHON_CMD"

    # Install build tools
    print_info "Installing build tools..."
    sudo apt update
    sudo apt install -y build-essential git

    # Check parent directory exists
    PARENT_DIR=$(dirname "$INSTALL_DIR")
    if [ ! -d "$PARENT_DIR" ]; then
        print_error "Parent directory $PARENT_DIR does not exist!"
        print_info "Please create it first or choose a different location."
        return
    fi

    # Check if parent directory is writable
    if [ ! -w "$PARENT_DIR" ]; then
        print_error "Parent directory $PARENT_DIR is not writable!"
        print_info "You may need sudo access or choose a different location."
        return
    fi

    # Check if directory exists
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists!"
        echo "Contents:"
        ls -lh "$INSTALL_DIR" 2>/dev/null | head -10
        echo ""
        read -p "Remove and continue? (y/n): " remove_confirm
        if [ "$remove_confirm" = "y" ] || [ "$remove_confirm" = "Y" ]; then
            print_info "Removing existing directory..."
            rm -rf "$INSTALL_DIR"
            print_success "Directory removed"
        else
            print_info "Cancelled"
            return
        fi
    fi

    # Clone WGP
    print_info "Cloning WGP (video_editor branch)..."
    git clone https://github.com/Tophness/Wan2GP.git -b video_editor "$INSTALL_DIR"
    print_success "WGP cloned!"

    cd "$INSTALL_DIR"

    # Clone Sage Attention
    print_info "Cloning Sage Attention..."
    git clone https://github.com/thu-ml/SageAttention.git
    print_success "Sage Attention cloned!"

    # Create venv
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    print_success "Virtual environment created!"

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip

    # Install build dependencies
    print_info "Installing build dependencies..."
    pip install packaging wheel setuptools

    # Install PyTorch
    print_info "Installing PyTorch with CUDA 12.8..."
    print_warning "This may take several minutes..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    print_success "PyTorch installed!"

    # Ask about Sage Attention
    echo ""
    print_info "Sage Attention requires CUDA toolkit to compile (15-30 minutes)"
    read -p "Install Sage Attention now? (y/n): " sage_confirm

    if [ "$sage_confirm" = "y" ] || [ "$sage_confirm" = "Y" ]; then
        cd SageAttention
        export EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32

        if python setup.py install 2>&1 | tee /tmp/sageattention_install.log; then
            print_success "Sage Attention installed!"
        else
            print_warning "Compilation failed, trying pre-built wheel..."
            pip install sageattention || print_warning "Sage Attention installation failed"
        fi
        cd "$INSTALL_DIR"
    else
        print_info "Skipping Sage Attention (you can install it later)"
    fi

    # Install WGP requirements
    print_info "Installing WGP requirements..."
    pip install -r requirements.txt
    print_success "WGP requirements installed!"

    # Create launcher
    print_info "Creating launcher script..."
    cat > run_wgp.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
source "$SCRIPT_DIR/venv/bin/activate"
python wgp.py "$@"
EOF
    chmod +x run_wgp.sh
    print_success "Launcher created!"

    # Update WGP_DIR for this session
    WGP_DIR="$INSTALL_DIR"
    VENV_DIR="$WGP_DIR/venv"

    echo ""
    print_header "Installation Complete!"
    echo "WGP installed at: $INSTALL_DIR"
    echo ""
    echo "To run WGP:"
    echo "  cd $INSTALL_DIR"
    echo "  ./run_wgp.sh"
    echo ""
}

# Main menu
show_menu() {
    clear
    print_header "WGP Manager - All-in-One Tool"
    echo "WGP Location: $WGP_DIR"
    echo ""
    echo "=== RUN & MANAGE ==="
    echo "1)  Run WGP"
    echo "2)  Update Git Repository"
    echo "3)  Update Python Dependencies"
    echo "4)  Update Both (Git + Python)"
    echo "5)  Check Status"
    echo ""
    echo "=== INSTALLATION ==="
    echo "6)  Fresh WGP Installation"
    echo "7)  Install CUDA Toolkit 12.8"
    echo "8)  Install/Reinstall Sage Attention"
    echo ""
    echo "=== UTILITIES ==="
    echo "9)  Find Available Drives"
    echo "10) Open WGP Directory (with venv)"
    echo "11) Change WGP Directory"
    echo "12) Exit"
    echo ""
}

# Change WGP directory
change_wgp_dir() {
    print_header "Change WGP Directory"
    echo "Current: $WGP_DIR"
    echo ""
    read -p "Enter new WGP directory path: " new_dir

    if [ -d "$new_dir" ]; then
        WGP_DIR="$new_dir"
        VENV_DIR="$WGP_DIR/venv"
        print_success "WGP directory changed to: $WGP_DIR"
    else
        print_error "Directory does not exist: $new_dir"
    fi
}

# Main loop
main() {
    # Don't check WGP dir on startup - allow fresh install

    while true; do
        show_menu
        read -p "Enter choice [1-12]: " choice
        echo ""

        case $choice in
            1)
                check_wgp_dir
                run_wgp
                ;;
            2)
                check_wgp_dir
                update_git
                read -p "Press Enter to continue..."
                ;;
            3)
                check_wgp_dir
                update_python
                read -p "Press Enter to continue..."
                ;;
            4)
                check_wgp_dir
                update_all
                read -p "Press Enter to continue..."
                ;;
            5)
                check_wgp_dir
                check_status
                read -p "Press Enter to continue..."
                ;;
            6)
                fresh_install
                read -p "Press Enter to continue..."
                ;;
            7)
                install_cuda
                read -p "Press Enter to continue..."
                ;;
            8)
                reinstall_sage
                read -p "Press Enter to continue..."
                ;;
            9)
                find_drives
                read -p "Press Enter to continue..."
                ;;
            10)
                check_wgp_dir
                open_directory
                ;;
            11)
                change_wgp_dir
                read -p "Press Enter to continue..."
                ;;
            12)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter 1-12."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Run main function
main

