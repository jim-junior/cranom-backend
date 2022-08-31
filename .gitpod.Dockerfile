# You can find the new timestamped tags here: https://hub.docker.com/r/gitpod/workspace-full/tags
FROM gitpod/workspace-full:latest

# Install custom tools, runtime, etc.
# install-packages is a wrapper for `apt` that helps skip a few commands in the docker env.
RUN sudo install-packages \
          binwalk \
          clang \
          tmux

RUN sudo apt-get update && sudo apt-get install -y ca-certificates curl

# Install k3d and kubectl

RUN sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

RUN sudo apt-get update
RUN sudo apt-get install -y kubectl

# Install pack-cli

RUN sudo add-apt-repository -y ppa:cncf-buildpacks/pack-cli

RUN sudo apt-get update

RUN sudo apt-get install pack-cli

RUN curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
