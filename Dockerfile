FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Install necessary packages, including OpenJDK 17 (available in Debian Bookworm)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    jq \
    openjdk-17-jdk  # Install OpenJDK 17

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# # Install latest Chrome
# RUN CHROME_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chrome[] | select(.platform == "linux64") | .url') \
#     && curl -sSLf --retry 3 --output /tmp/chrome-linux64.zip "$CHROME_URL" \
#     && unzip /tmp/chrome-linux64.zip -d /opt \
#     && ln -s /opt/chrome-linux64/chrome /usr/local/bin/chrome \
#     && chmod +x "/usr/local/bin/chrome" \
#     && rm /tmp/chrome-linux64.zip

# # Install latest chromedriver
# RUN CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url') \
#     && curl -sSLf --retry 3 --output /tmp/chromedriver-linux64.zip "$CHROMEDRIVER_URL" \
#     && unzip -o /tmp/chromedriver-linux64.zip -d /tmp \
#     && rm -rf /tmp/chromedriver-linux64.zip \
#     && mv -f /tmp/chromedriver-linux64/chromedriver "/usr/local/bin/chromedriver" \
#     && chmod +x "/usr/local/bin/chromedriver"

# RUN apt-get update -y
# RUN apt-get install -y libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libatk1.0-0 libatk-bridge2.0-0 libgbm-dev libgtk-3.0 libcups2 libasound2
# RUN apt-get install -y ca-certificates fonts-liberation libappindicator3-1 libc6
# RUN apt-get install -y libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 
# RUN apt-get install -y libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 
# RUN apt-get install -y libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils

# Install Allure 2.24 manually
RUN wget https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.zip -O /tmp/allure.zip && \
    unzip /tmp/allure.zip -d /opt/ && \
    ln -s /opt/allure-2.24.0/bin/allure /usr/local/bin/allure && \
    chmod +x /usr/local/bin/allure && \
    rm /tmp/allure.zip

# # Set up the XVFB server for running Chrome in headless mode
# RUN apt-get install -y xvfb
# RUN Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &


# Set up app code
RUN mkdir /automation_app
WORKDIR /automation_app
COPY ./requirements.txt /automation_app
COPY ./automation_app /automation_app

# Install Python dependencies
# RUN pip install --no-cache-dir -r ./requirements.txt
RUN pip install -r ./requirements.txt

CMD ["python", "flask_app.py"]
#CMD ["xvfb-run"]