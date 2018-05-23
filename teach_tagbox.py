import base64
import os
import requests

IP = 'localhost'
PORT = '8080'
CLASSIFIER = 'tagbox'
TARGET = 'tag'

teach_api_url = "http://{}:{}/{}/teach".format(IP, PORT, CLASSIFIER)
health_api_url = "http://{}:{}/readyz".format(IP, PORT)


def _extract_base64_contents(image_file):
    return base64.b64encode(image_file.read()).decode('ascii')


def main():
    failed_images_list = []
    total_succeeded = 0
    total_failed = 0
    try:
        json_response = requests.get(health_api_url)
    except requests.exceptions.RequestException as e:
        print("{} is unreachable......... Please check if it's up and running! ".format(CLASSIFIER))
        print(e)
    else:
        if json_response.status_code == 200:
            folders = [dir for dir in os.listdir('.')
                       if os.path.isdir(os.path.join('.', dir)) and not dir.startswith('.')]

            # ID's here are just integers you can replace this by any other number. You can also edit this and make the
            # ID's be for example names of the folders (in case they are numbers)
            i = 1
            # sort the folder names alphabetically
            folders.sort(key=str.lower)
            for folder_name in folders:
                succeeded = 0
                total = 0
                print("Started training for " + folder_name)
                for file in os.listdir(os.getcwd() + "/" + folder_name):
                    total += 1
                    if file.endswith(('.jpg', '.png', '.jpeg')):
                        json_data = {
                            TARGET: folder_name,
                            "id": i
                        }
                        print(
                            "Sending request to " + teach_api_url + " to train it with this file "
                            + file + " with tag = " + folder_name)

                        json_response = (requests.post(
                            teach_api_url,
                            data=json_data,
                            files={'file': open(folder_name + '/' + file, 'rb')}
                        ))

                        if json_response.status_code == 200:
                            print("Training for " + file + " has succeeded! ")
                            succeeded += 1

                        elif json_response.status_code == 400:
                            print(json_response.text + " on the following image " + file)
                            failed_images_list.append(json_response.text + " on the following image " + file)
                        else:
                            print("Something went wrong! Please check the docker instance if it's alive")

                print(" The training for " + folder_name + " has succeeded for " + str(
                    succeeded) + " images! " + ", but failed to train  " + str(total - succeeded) + " images !")
                i += 1
                total_succeeded += succeeded
                total_failed += total - succeeded
            print("Total succeeded trainings/images is: ", total_succeeded)
            print("Total failed trainings/images is: ", total_failed)
            with open('failed_log.txt', 'w') as log_file:
                for failed_image in failed_images_list:
                    log_file.write("%s\n" % failed_image)

        else:
            print("{} isn't ready! Please check if the docker instance is up an running!".format(CLASSIFIER))


if __name__ == '__main__':
    main()
