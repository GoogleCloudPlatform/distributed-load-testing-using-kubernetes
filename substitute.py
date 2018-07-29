import argparse


def replace_in_file(filename, target, replacement):
  with open(filename) as f:
    lines = [line.rstrip() for line in f.readlines()]

  with open(filename, 'w+') as f:
    for line in lines:
      f.write(line.replace(target, replacement) + '\n')

def change_target_url(target_url):
    replace_in_file('k8s/environment-variable.yaml', '$targetUrl',
                  target_url)  

def change_image(project_id, image_name, image_tag):
  replace_in_file('k8s/locust-master-deployment.yaml', '$appImage',
                  'gcr.io/{project_id}/{image_name}:{image_tag}'.format(
                      project_id=project_id,
                      image_name=image_name,
                      image_tag=image_tag))
  replace_in_file('k8s/locust-worker-deployment.yaml', '$appImage',
                  'gcr.io/{project_id}/{image_name}:{image_tag}'.format(
                      project_id=project_id,
                      image_name=image_name,
                      image_tag=image_tag)) 

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--project-id")
  parser.add_argument("--image-name")
  parser.add_argument("--image-tag")
  parser.add_argument("--target-url")
  result = parser.parse_args()

  change_image(result.project_id, result.image_name,
               result.image_tag)
  change_target_url(result.target_url)
