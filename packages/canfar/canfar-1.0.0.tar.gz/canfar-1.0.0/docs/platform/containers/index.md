# Containers

**Working with astronomy software containers on CANFAR - understanding container environments, using pre-built images, and creating custom software stacks.**

!!! info "Platform Navigation"
    **Containers**: Software environments and containerised applications for astronomy.  
    **[Platform Home](../index.md)** | **[Platform Concepts](../concepts.md)** | **[Interactive Sessions](../sessions/index.md)** | **[Storage Systems](../storage/index.md)** | **[Support](../support/index.md)**

!!! abstract "🎯 Container Guide Overview"
    **Master CANFAR's containerised environments:**
    
    - **[Container Concepts](#what-are-containers)**: Understanding reproducible software environments
    - **[Available Containers](#canfar-supported-containers)**: Pre-built astronomy software stacks
    - **[Container Building](build.md)**: Creating custom environments for specialised workflows
    - **[Registry Management](registry.md)**: Harbor registry access and image distribution

Containers provide pre-packaged software environments that include everything needed to run astronomy applications. On CANFAR, containers eliminate the "works on my machine" problem by ensuring consistent, reproducible computational environments across different sessions and workflows.

## 📋 What Are Containers?

Think of containers as complete software packages that bundle an operating system (typically Ubuntu Linux), astronomy software like CASA or Python packages, programming tools, system libraries, and environment configuration into a single portable unit. When you launch a session on CANFAR, you're essentially starting up one of these pre-configured environments with your data and home directory automatically mounted and accessible.

!!! success "Key Concept: Reproducible Environments"
    Containers provide consistent, reproducible software environments for astronomy work across sessions and teams.

### Why Containers Matter for Astronomy

#### Traditional Software Installation

- Struggle with dependencies and conflicting versions
- Missing libraries and system requirements
- Different behaviour across different machines
- Time-consuming setup and configuration

#### CANFAR Containers

- **Consistent environment**: Works the same everywhere
- **Pre-configured**: Astronomy packages included
- **No installation hassles**: Ready to use immediately
- **Easy sharing**: Reproducible results across teams

!!! tip "Research Reproducibility"
    Containers ensure your analysis runs the same way for you, your collaborators, and future researchers. This is crucial for reproducible science.

### Container Architecture on CANFAR

The container ecosystem on CANFAR follows a layered approach:

```mermaid
graph TB
    BaseOS[Ubuntu Linux Base] --> SystemLibs[System Libraries]
    SystemLibs --> CondaPython[Conda + Python]
    CondaPython --> AstroLibs[Astronomy Libraries]
    AstroLibs --> SpecializedTools[Specialized Tools]
    
    SpecializedTools --> Astroml[astroml Container]
    SpecializedTools --> Casa[casa Container]
    SpecializedTools --> Custom[Custom Containers]
    
    Runtime[CANFAR Runtime] --> Storage[Storage Mounting]
    Runtime --> UserContext[User Context]
    Runtime --> Resources[Resource Allocation]
```

**Base containers** provide fundamental tools and the conda package manager, while **specialised containers** build upon these foundations to offer domain-specific software stacks. This architecture ensures consistency while allowing flexibility for different research needs.

## 🏗️ Build Time vs Runtime

Understanding the distinction between build time and runtime is crucial for effective container usage:

### Build Time
**What happens when containers are created:**

- **Base image selection**: Choose Ubuntu, Python, or specialized astronomy base
- **Software installation**: Install system packages, Python libraries, astronomy tools
- **Environment configuration**: Set up paths, environment variables, user permissions
- **Code packaging**: Include stable scripts and analysis tools
- **Image optimisation**: Layer caching, size reduction, security patches

```dockerfile
# Build time example
FROM ubuntu:22.04

# Install system dependencies (build time)
RUN apt-get update && apt-get install -y \
    python3-dev \
    libfitsio-dev \
    && apt-get clean

# Install Python packages (build time)
RUN pip install astropy numpy matplotlib

# Package stable code (build time)
COPY analysis_tools/ /opt/tools/
```

### Runtime
**What happens when you launch a session:**

- **User context**: Container runs as your CADC username (not root)
- **Storage mounting**: `/arc/home/`, `/arc/projects/`, `/scratch/` mounted automatically
- **Resource allocation**: CPU, memory, GPU assigned based on session request
- **Network access**: Internet connectivity for downloading data or documentation
- **Session integration**: Jupyter, desktop, or headless execution mode activated

```bash
# Runtime environment (inside your running container)
echo $USER                      # [user]
echo $HOME                      # /arc/home/[user]
ls /arc/projects/               # Your accessible project directories
df -h /scratch/                 # Temporary high-speed storage
```

!!! warning "Persistence Boundary"
    **Build time changes** are permanent and part of the container image. **Runtime changes** (like `pip install --user package`) are temporary and lost when the session ends. Keep stable software in the image; keep development scripts in `/arc/`.

## 🔗 How Containers Relate to Sessions

CANFAR containers are designed to work seamlessly with different session types, each optimised for specific workflows:

### Session Type Integration

```mermaid
graph TB
    Container[Container Image] --> SessionType{Session Type}
    
    SessionType --> Notebook[Notebook Session]
    SessionType --> Desktop[Desktop Session]
    SessionType --> Batch[Batch/Headless Session]
    SessionType --> Contributed[Contributed Session]
    
    Notebook --> JupyterLab[JupyterLab Interface]
    Desktop --> DesktopEnv[Ubuntu Desktop GUI]
    Batch --> ScriptExec[Script Execution]
    Contributed --> WebApp[Custom Web App]
    
    JupyterLab --> Storage[/arc/ Storage]
    DesktopEnv --> Storage
    ScriptExec --> Storage
    WebApp --> Storage
```

**Same container, different interfaces**: The `astroml` container can run as a notebook (JupyterLab), desktop application (terminal), or batch job (headless script execution).

### Notebook Sessions

**Requirements for notebook containers:**

1. **JupyterLab installed**: The `jupyterlab` package must be available
2. **Container labelling**: Tagged as `notebook` in the registry

When you launch a notebook session, CANFAR automatically:
- Starts JupyterLab on port 8888
- Mounts your storage directories
- Provides web-based access to the Python environment

**The `astroml` container** exemplifies this perfectly - it's a comprehensive Python astronomy stack with Astropy, SciPy, pandas, scikit-learn, PyTorch, and many more packages pre-installed.

```bash
# Check installed packages in a running astroml container
mamba list                     # Conda/mamba installed packages  
apt list --installed           # System packages (Ubuntu)
ls /build_info/                # Container build information
```

**Runtime package installation:**
```bash
# Install Python packages at runtime (saved to /arc/home/)
pip install fireducks

# Show where it was installed
pip show -f fireducks           # Should show ~/.local/lib/python*/
```

!!! tip "GPU Support"
    For GPU acceleration, use the `astroml-cuda` container which extends `astroml` with CUDA libraries and GPU-enabled PyTorch, PyArrow, and other frameworks.

### Desktop Application Sessions

Desktop sessions integrate containers in two ways:

#### 1. Base Desktop Container
The core **desktop** container provides the Ubuntu desktop environment with Firefox, file managers, and terminals. This runs as your main desktop session.

#### 2. Desktop-App Containers
Specialised containers that run specific GUI applications within desktop sessions.

**Requirements for desktop-app containers:**

1. **X11/Xorg application**: Must have at least one GUI application (minimum: `xterm`)
2. **Startup script**: Application launcher at `/skaha/startup.sh`
3. **Container labelling**: Tagged as `desktop-app` in the registry

**How it works:**
- Each desktop-app container runs on its own worker node
- Applications connect to your desktop session via X11 forwarding
- Shared storage provides data access across all containers
- Applications appear in the **Astro Software** menu

```bash
# Example desktop-app startup script (/skaha/startup.sh)
#!/bin/bash
export DISPLAY=${DISPLAY}
cd /arc/home/$USER
exec your-gui-application
```

The same **astroml** container can run as both notebook (has JupyterLab) and desktop-app (has xterm), demonstrating the flexibility of container usage.

### Batch/Headless Sessions

Headless containers execute without graphical interfaces, perfect for automated processing:

- **No GUI requirements**: Command-line tools only
- **Script execution**: Runs your specified command and exits
- **Background processing**: Perfect for large datasets and automation
- **Resource optimisation**: Can use different resource priorities

```bash
# Example headless execution
python /arc/projects/[project]/scripts/reduce_data.py --input=/arc/projects/[project]/data/ --output=/arc/projects/[project]/results/
```

### Contributed Application Sessions

Contributed applications are custom web-based tools that integrate with CANFAR:

**Requirements:**
1. **Web service**: Application serves HTTP on port 5000
2. **Startup script**: Service launcher at `/skaha/startup.sh`
3. **Container labelling**: Tagged appropriately for discovery

Examples include Marimo (reactive notebooks) and VSCode (browser IDE).

## 💾 Storage Mounting and Integration

### CANFAR Storage Integration

CANFAR automatically mounts storage systems into your container at runtime, providing seamless access to persistent data:

```mermaid
graph LR
    Container[Running Container] --> ArcMount[/arc/ Mount Point]
    
    ArcMount --> Home[/arc/home/[user]/]
    ArcMount --> Projects[/arc/projects/[project]/]
    
    Container --> Scratch[/scratch/]
    Container --> Tmp[/tmp/]
    
    Home --> HomeData[(Personal Data<br/>10GB Quota)]
    Projects --> ProjectData[(Shared Project Data<br/>Variable Quota)]
    Scratch --> FastStorage[(Fast Temporary Storage<br/>Node-local)]
    Tmp --> TempFiles[(Temporary Files<br/>Container-local)]
```

#### Storage Hierarchy

| Mount Point | Purpose | Persistence | Quota | Sharing |
|-------------|---------|-------------|-------|---------|
| `/arc/home/[user]/` | Personal files, notebooks, configs | Permanent | 10GB | Private |
| `/arc/projects/[project]/` | Research data, collaboration | Permanent | Variable | Team-based |
| `/scratch/` | High-speed processing | Session only | Node-dependent | Private |
| `/tmp/` | Temporary files | Session only | Limited | Private |

#### Storage Best Practices

**Personal Development (`/arc/home/`):**
```bash
/arc/home/[user]/
├── notebooks/              # Jupyter notebooks
├── scripts/               # Analysis scripts  
├── .local/               # pip install --user packages
├── .config/              # Application configurations
└── small_datasets/       # Personal research data
```

**Project Collaboration (`/arc/projects/`):**
```bash
/arc/projects/[project]/
├── raw_data/             # Input datasets
├── processed/            # Reduced data products
├── scripts/              # Shared analysis code
├── docs/                 # Project documentation
└── results/              # Final outputs
```

**Temporary Processing (`/scratch/`):**
```bash
# Copy large datasets to fast storage for processing
cp /arc/projects/survey/large_data.fits /scratch/
process_data /scratch/large_data.fits /scratch/output.fits
cp /scratch/output.fits /arc/projects/survey/results/
```

### User Context and Permissions

Containers run with your CADC user identity, not as root or container-defined users:

```bash
# Inside any CANFAR container
whoami                    # [user]
id                        # uid=1234([user]) gid=1234([user]) groups=[user](and-all-your-CADC-groups)
echo $HOME                # /arc/home/[user]
groups                    # Shows your CANFAR project group memberships
```

**Security model:**
- **No root access**: Containers cannot perform system administration
- **File permissions**: Respect standard Unix permissions on `/arc/`
- **Group membership**: Access to `/arc/projects/` based on CANFAR group membership
- **Network isolation**: Containers have internet access but cannot access other users' sessions

## 🔧 CANFAR-Supported Containers

The CANFAR team maintains several core containers that cover most astronomy research needs:

### Core Astronomy Containers

#### `astroml` - General Astronomy Analysis

**Purpose**: Comprehensive Python environment for most astronomy workflows

**Pre-installed software:**
- **Python stack**: numpy, scipy, matplotlib, pandas, jupyter, pyarrow
- **Astronomy libraries**: astropy, astroquery, photutils, reproject
- **Machine learning**: scikit-learn, pytorch
- **Data formats**: FITS, HDF5
- **Development tools**: Git, vim, nano, SSH client

**Best for:**
- Python-based data analysis and visualisation
- Statistical analysis and machine learning
- Multi-wavelength astronomy workflows
- Educational and tutorial sessions

```bash
# Launch astroml notebook session
canfar launch notebook images.canfar.net/skaha/astroml:latest \
  --name "data-analysis" --cores 4 --memory 16
```

#### `astroml-cuda` - GPU-Accelerated Analysis

**Purpose**: Extends `astroml` with GPU computing capabilities

**Additional features:**
- **CUDA libraries**: NVIDIA CUDA toolkit and drivers
- **GPU frameworks**: all cuda-enabled frameworks of the astroml container

**Best for:**
- Machine learning with large datasets
- Image processing and computer vision
- Simulation and N-body computations
- Deep learning applications

#### `casa` - Radio Astronomy

**Purpose**: Specialised environment for radio interferometry analysis

**Pre-installed software:**
- **CASA suite**: Complete Common Astronomy Software Applications
- **Python integration**: CASA Python bindings and tasks
- **Data formats**: Measurement Set, FITS-IDI, UVFITS support
- **Visualisation**: CASA plotting and imaging tools

**Best for:**
- Radio interferometry data reduction
- Synthesis imaging and deconvolution
- Calibration and flagging workflows
- Single-dish radio astronomy

```bash
# Launch CASA desktop session for GUI tools
canfar create desktop images.canfar.net/skaha/casa:latest \
  --name "vla-reduction" --cores 8 --memory 32
```

### Visualisation Containers

#### `carta` - Radio Astronomy Visualisation

**Purpose**: Interactive visualisation of radio astronomy data

**Features:**
- **CARTA application**: Cube Analysis and Rendering Tool for Astronomy
- **Multi-dimensional data**: Spectral cubes, moment maps, polarisation
- **Interactive analysis**: Region statistics, profile extraction
- **Collaboration support**: Session sharing capabilities

#### `firefly` - Optical Survey Data

**Purpose**: Advanced visualisation for optical and infrared surveys

**Features:**
- **Multi-mission support**: LSST, Spitzer, WISE, 2MASS data
- **Interactive catalogues**: Source overlays and cross-matching
- **Multi-wavelength workflows**: RGB composites and band comparisons
- **Large dataset handling**: Efficient rendering of survey-scale data

### Development and Desktop Containers

#### `desktop` - Ubuntu Environment

**Purpose**: Complete Linux desktop for GUI applications and legacy software

**Features:**
- **Ubuntu 22.04 LTS**: Linux environment
- **Desktop environment**: Full GNOME-based interface
- **Applications**: Firefox, file managers, terminals, editors
- **X11 forwarding**: Support for launching astronomy GUI applications

#### `notebook` - Jupyter Environment

**Purpose**: Minimal Jupyter environment for basic Python work

**Features:**
- **Core Python**: NumPy, SciPy, Matplotlib basics
- **Jupyter Lab**: Web-based notebook interface
- **Extensible**: Foundation for custom development
- **Fast startup**: Minimal software for quick sessions

### Container Selection Guide

| Workflow Type | Recommended Container | Session Type | Typical Resources |
|---------------|----------------------|--------------|-------------------|
| **Python data analysis** | `astroml` | Notebook | 2-4 cores, 8-16GB |
| **GPU machine learning** | `astroml-cuda` | Notebook | 4-8 cores, 16-32GB, 1 GPU |
| **Radio interferometry** | `casa` | Notebook/Desktop | 4-8 cores, 16-32GB |
| **Radio data visualisation** | `carta` | CARTA session | 2-4 cores, 8-16GB |
| **Optical survey analysis** | `firefly` | Firefly session | 2-4 cores, 8-16GB |
| **GUI applications** | `desktop` | Desktop | 2-4 cores, 8-16GB |
| **Legacy software** | `desktop` | Desktop | Variable |
| **Batch processing** | `astroml`/`casa` | Headless | Variable |

!!! tip "Container Selection Strategy"
    Start with `astroml` for most astronomy work. It includes comprehensive libraries and is actively maintained. Use specialised containers (`casa`, `carta`, `firefly`) only when you need their specific tools.

### Version Management

CANFAR containers follow semantic versioning:

- **`:latest`** - Current stable release (recommended for most work)
- **`:YY.MM`** - Monthly snapshots for reproducibility
- **`:commit-hash`** - Specific builds for exact reproducibility

```bash
# Use latest stable version (recommended)
images.canfar.net/skaha/astroml:latest

# Use specific monthly snapshot for reproducible research
images.canfar.net/skaha/astroml:25.09

# Use exact commit for critical reproducibility
images.canfar.net/skaha/astroml:a1b2c3d4
```

### Container Updates and Maintenance

CANFAR containers receive regular updates:

**Monthly releases**: Security patches, library updates, new features
**Quarterly reviews**: Major version updates, new software additions
**Community feedback**: Feature requests and bug reports incorporated

**Update notifications:**
- Science Portal notifications for major changes

!!! warning "Version Pinning for Reproducibility"
    For published research, specify exact container versions (monthly tags or commit hashes) to ensure long-term reproducibility of your analysis.
