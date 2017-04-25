import boto3

credential = {}


def back_db():
    """
    备份数据库到Amazon S3
    """
    with open("credential", "r", encoding="utf8") as credentialFile:
        for line in credentialFile:
            items = line.split(":")
            credential[items[0].strip()] = items[1].strip()
    my_session = boto3.session.Session(aws_access_key_id=credential["aws_access_key_id"],
                                       aws_secret_access_key=credential["aws_secret_access_key"])
    s3 = my_session.resource("s3")
    for bucket in s3.buckets.all():
        print(bucket.name)
