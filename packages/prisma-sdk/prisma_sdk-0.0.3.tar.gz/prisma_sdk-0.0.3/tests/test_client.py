from prisma_sdk import PrismaAPI


client = PrismaAPI(auth_token="LeoGianluKey", base_url="https://mwuamhsio56zkuxyerq62fdzom0vxeeh.lambda-url.us-east-2.on.aws/")

response = client.send_model_data(
    question="What is 2+2?",
    answer="4",
    model_id=1,
    url="https://iltxuzu45yszh3uf7gdjdc2nni0ueqox.lambda-url.us-east-2.on.aws/"
)

import json
print(json.dumps(response, indent=2))
