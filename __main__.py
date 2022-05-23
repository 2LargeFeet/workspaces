import pulumi
import pulumi_aws as aws

config = pulumi.Config()

workspaces = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    actions=["sts:AssumeRole"],
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="Service",
        identifiers=["workspaces.amazonaws.com"],
    )],
)])
workspaces_default = aws.iam.Role("workspacesDefault", assume_role_policy=workspaces.json)
workspaces_default_service_access = aws.iam.RolePolicyAttachment("workspacesDefaultServiceAccess",
    role=workspaces_default.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonWorkSpacesServiceAccess")
workspaces_default_self_service_access = aws.iam.RolePolicyAttachment("workspacesDefaultSelfServiceAccess",
    role=workspaces_default.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonWorkSpacesSelfServiceAccess")
contractor_vpc = aws.ec2.Vpc("contractorVpc", cidr_block="10.0.0.0/16")
contractor_c = aws.ec2.Subnet("contractorC",
    vpc_id=contractor_vpc.id,
    availability_zone="us-east-1c",
    cidr_block="10.0.2.0/24")
contractor_d = aws.ec2.Subnet("contractorD",
    vpc_id=contractor_vpc.id,
    availability_zone="us-east-1d",
    cidr_block="10.0.3.0/24")
allow_tls = aws.ec2.SecurityGroup("allowTls",
    description="Allow TLS inbound traffic",
#    vpc_id=contractor_vpc["main"]["id"],
#    vpc_id=contractor_vpc["contractorVpc"]["id"],
    vpc_id=contractor_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="TLS from VPC",
        from_port=443,
        to_port=443,
        protocol="tcp",
        cidr_blocks=[contractor_vpc.cidr_block],
#        ipv6_cidr_blocks=[contractor_vpc["main"]["ipv6_cidr_block"]],
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    tags={
        "Name": "allow_tls",
    })
contractor_directoryservice_directory_directory = aws.directoryservice.Directory("contractorDirectoryservice/directoryDirectory",
    name="workspace.gombocom.com",
    password=config.require_secret('password'),
    size="Small",
    vpc_settings=aws.directoryservice.DirectoryVpcSettingsArgs(
        vpc_id=contractor_vpc.id,
        subnet_ids=[
            contractor_a.id,
            contractor_b.id,
        ],
    ))
#contractor_directoryservice = ""
contractor_directory = aws.workspaces.Directory("contractorDirectory",
#    directory_id=contractor_directoryservice / directory_directory["id"],
    directory_id=contractor_directoryservice_directory_directory.id,
#    directory_id=contractor_directoryservice,
    subnet_ids=[
        contractor_c.id,
        contractor_d.id,
    ],
    tags={
        "security": "true",
    },
    self_service_permissions=aws.workspaces.DirectorySelfServicePermissionsArgs(
        change_compute_type=False,
        increase_volume_size=False,
        rebuild_workspace=False,
        restart_workspace=True,
        switch_running_mode=False,
    ),
    workspace_access_properties=aws.workspaces.DirectoryWorkspaceAccessPropertiesArgs(
        device_type_android="DENY",
        device_type_chromeos="ALLOW",
        device_type_ios="DENY",
        device_type_linux="DENY",
        device_type_osx="ALLOW",
        device_type_web="ALLOW",
        device_type_windows="ALLOW",
        device_type_zeroclient="DENY",
    ),
    workspace_creation_properties=aws.workspaces.DirectoryWorkspaceCreationPropertiesArgs(
#        custom_security_group_id=aws_security_group["contractor"]["id"],
        custom_security_group_id=allow_tls.id,
        default_ou="OU=AWS,DC=Workgroup,DC=contractor,DC=com",
        enable_internet_access=True,
        enable_maintenance_mode=True,
        user_enabled_as_local_administrator=True,
    ),
    opts=pulumi.ResourceOptions(depends_on=[
            workspaces_default_service_access,
            workspaces_default_self_service_access,
        ]))
contractor_a = aws.ec2.Subnet("contractorA",
    vpc_id=contractor_vpc.id,
    availability_zone="us-east-1a",
    cidr_block="10.0.0.0/24")
contractor_b = aws.ec2.Subnet("contractorB",
    vpc_id=contractor_vpc.id,
    availability_zone="us-east-1b",
    cidr_block="10.0.1.0/24")
#contractor_directoryservice_directory_directory = aws.directoryservice.Directory("contractorDirectoryservice/directoryDirectory",
#    name="workspace.gombocom.com",
#    password=config.require_secret('password'),
#    size="Small",
#    vpc_settings=aws.directoryservice.DirectoryVpcSettingsArgs(
#        vpc_id=contractor_vpc.id,
#        subnet_ids=[
#            contractor_a.id,
#            contractor_b.id,
#        ],
#    ))
#contractor_ip_group = aws.workspaces.IpGroup("contractorIpGroup")
#contractor_directory = aws.workspaces.Directory("contractorDirectory",
#    directory_id=aws_directory_service_directory["contractor"]["id"],
#    ip_group_ids=[contractor_ip_group.id])
#value_windows10 = aws.workspaces.get_bundle(bundle_id="wsb-bh8rsxt14")
#contractor = aws.workspaces.Workspace("contractor",
#    directory_id=aws_workspaces_directory["contractor"]["id"],
#    bundle_id=value_windows10.id,
#    user_name="john.doe",
#    root_volume_encryption_enabled=True,
#    user_volume_encryption_enabled=True,
#    volume_encryption_key="alias/aws/workspaces",
#    workspace_properties=aws.workspaces.WorkspaceWorkspacePropertiesArgs(
#        compute_type_name="VALUE",
#        user_volume_size_gib=10,
#        root_volume_size_gib=80,
#        running_mode="AUTO_STOP",
#        running_mode_auto_stop_timeout_in_minutes=60,
#    ),
#    tags={
#        "Department": "IT",
#    })

# pulumi.export('bucket_name',  bucket.id)