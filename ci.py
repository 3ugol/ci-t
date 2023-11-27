import git
import subprocess
import configparser
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return (config['DEFAULT']['remo_git_repo'], config['DEFAULT']['branch'], 
            config['DEFAULT']['local_git_repo'], config['EMAIL']['sender'], 
            config['EMAIL']['receiver'], config['EMAIL']['smtp_server'], 
            config['EMAIL']['smtp_port'], config['EMAIL']['smtp_user'], 
            config['EMAIL']['smtp_password'])

def fetch_changes(remote_repo_url, branch, local_repo_path):
    if not os.path.exists(local_repo_path):
        os.makedirs(local_repo_path)
        git.Repo.clone_from(remote_repo_url, local_repo_path, branch=branch)
    else:
        repo = git.Repo(local_repo_path)
        origin = repo.remotes.origin
        origin.fetch()
        changes = list(repo.iter_commits(f'{branch}..origin/{branch}'))
        return changes
    # Same as before

def execute_build_script(script_path):
    try:
        subprocess.run([script_path], shell=True, check=True)
    #    subprocess.run(script_path, shell=True)
    except subprocess.CalledProcessError as e:
        return e
    return None

def send_email(sender, receiver, smtp_server, smtp_port, smtp_user, smtp_password, message):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "Build Process Failed"
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    config_path = 'C:\\home_work3\\.conf'
    (remote_repo_url, branch, local_repo_path, sender, receiver, smtp_server, 
     smtp_port, smtp_user, smtp_password) = read_config(config_path)

    changes = fetch_changes(remote_repo_url, branch, local_repo_path)
    if changes:
        print("Виявлено зміни. Запуск build.bat...")
        error = execute_build_script(os.path.join(local_repo_path, '..\\build.bat'))
        if error:
            print("Виникла помилка під час виконання build.bat.")
            send_email(sender, receiver, smtp_server, smtp_port, smtp_user, smtp_password, 
                       f"Помилка під час виконання build.bat: {error}")
    else:
        print("Змін не виявлено.")

if __name__ == "__main__":
    main()
