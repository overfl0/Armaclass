FROM debian:12-slim

RUN apt update && \
    apt install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev && \
    apt install -y \
    git \
    wget \
    xz-utils \
    libtinfo5 \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR "/app"
ENV CLANG_DIR "$APP_DIR/clang"
RUN mkdir $APP_DIR
RUN mkdir $CLANG_DIR
WORKDIR $APP_DIR

ARG CLANG_URL=https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/clang+llvm-17.0.6-x86_64-linux-gnu-ubuntu-22.04.tar.xz
#ARG CLANG_URL=https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.4/clang+llvm-18.1.4-x86_64-linux-gnu-ubuntu-18.04.tar.xz
ARG CLANG_CHECKSUM=884ee67d647d77e58740c1e645649e29ae9e8a6fe87c1376be0f3a30f3cc9ab3
#ARG CLANG_CHECKSUM=1607375b4aa2aec490b6db51846a04b265675a87e925bcf5825966401ff9b0b1

ENV CLANG_FILE clang.tar.xz
RUN wget -q -O $CLANG_FILE $CLANG_URL && \
    echo "$CLANG_CHECKSUM  $CLANG_FILE" | sha256sum -c - && \
    tar xf $CLANG_FILE -C $CLANG_DIR --strip-components 1 && \
    rm $CLANG_FILE

# https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#step-1-compiling-your-extension
ENV CC "$CLANG_DIR/bin/clang"
ENV CXX "$CLANG_DIR/bin/clang++"
ENV LDSHARED "$CLANG_DIR/bin/clang -shared"

RUN wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar xzf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure && \
    make -j "$(nproc)" && \
    make altinstall bininstall

RUN python3 --version

ENV VIRTUAL_ENV "/opt/venv"
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

# https://github.com/google/atheris#building-from-source
RUN LIBFUZZER_LIB=$($CLANG_DIR/bin/clang -print-file-name=libclang_rt.fuzzer_no_main.a) \
    python3 -m pip install --no-binary atheris atheris

ARG BRANCH=master

## https://github.com/agronholm/cbor2
#ENV CBOR2_BUILD_C_EXTENSION "1"
#RUN git clone --branch $BRANCH https://github.com/agronholm/cbor2.git
#RUN python3 -m pip install cbor2/

COPY ["build.py", "setup_cython.py", "requirements-*.txt", "./"]
COPY ["armaclass", "armaclass"]
RUN python -m pip install -r requirements-dev.txt

ENV CFLAGS "-fsanitize=address,undefined,fuzzer-no-link"
ENV CXXFLAGS "-fsanitize=address,undefined,fuzzer-no-link"
#ENV CFLAGS "-fsanitize=undefined,fuzzer-no-link"
#ENV CXXFLAGS "-fsanitize=undefined,fuzzer-no-link"
RUN python setup_cython.py build_ext --inplace --force

# Allow Atheris to find fuzzer sanitizer shared libs
# https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#option-a-sanitizerlibfuzzer-preloads
#ENV LD_PRELOAD "$VIRTUAL_ENV/lib/python3.11/site-packages/asan_with_fuzzer.so"
ENV LD_PRELOAD "$VIRTUAL_ENV/lib/python3.11/site-packages/ubsan_cxx_with_fuzzer.so"

# Subject to change by upstream, but it's just a sanity check
#RUN nm $(python3 -c "import armaclass.parser; print(armaclass.parser.__file__)") | grep asan \
#    && echo "Found ASAN" \
#    || (echo "Missing ASAN" && false)

# 1. Skip allocation failures and memory leaks for now, they are common, and low impact (DoS)
# 2. https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#leak-detection
# 3. Provide the symbolizer to turn virtual addresses to file/line locations
ENV ASAN_OPTIONS "allocator_may_return_null=1,detect_leaks=0,external_symbolizer_path=$CLANG_DIR/bin/llvm-symbolizer"

COPY fuzz.py fuzz.py

#ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["python3", "fuzz.py"]
CMD ["-help=1"]

# docker build --build-arg BRANCH=5.5.1 -t cbor2-fuzz -f Dockerfile .
# docker run -it -v $(pwd):/tmp/output/ cbor2-fuzz
# docker run -v $(pwd):/tmp/output/ cbor2-fuzz -artifact_prefix=/tmp/output/