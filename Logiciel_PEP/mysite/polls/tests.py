from django.test import TestCase
<<<<<<< HEAD

# Create your tests here.
=======
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from .models import MyModel

class FileUploadTest(TestCase):
    def test_file_upload_to_s3(self):
        # Créez une instance de votre modèle
        my_instance = MyModel()

        # Simulez un fichier à uploader
        file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")

        # Assigne le fichier simulé à votre champ FileField ou ImageField
        my_instance.file_field = file

        # Sauvegardez l'instance pour effectuer l'upload
        my_instance.save()

        # Vérifiez que le fichier existe dans S3
        # Vous pouvez utiliser boto3 pour vérifier cela
        import boto3
        s3 = boto3.client('s3', aws_access_key_id='your_access_key', aws_secret_access_key='your_secret_key')
        response = s3.get_object(Bucket='your_bucket_name', Key='path/to/your/file.txt')
        
        self.assertIn('ContentType', response)
        self.assertEqual(response['ContentType'], 'text/plain')
>>>>>>> refs/remotes/origin/main
