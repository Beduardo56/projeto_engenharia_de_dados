from aws_cdk import core
from aws_cdk import aws_rds as rds, aws_ec2 as ec2
from projeto_engenharia_de_dados import active_environment


class CommonStack(core.Stack):
    """
    This project aims to construct a MySQL database in production
    """
    def __init__(self, scope: core.Construct, **kwargs) -> None:
        self.deploy_env = active_environment
        super().__init__(scope, id=f"{self.deploy_env.value}-common-stack", **kwargs)

        self.custom_vpc = ec2.Vpc(self, f"vpc-{self.deploy_env.value}")
        # Defining a security group in my VPC
        self.covid_rds_sg = ec2.SecurityGroup(
            self,
            f"covid-{self.deploy_env.value}-sg",
            vpc=self.custom_vpc,
            allow_all_outbound=True,
            security_group_name=f"covid-{self.deploy_env.value}-sg",
        )
        # All Ip can ingress in my security group
        self.covid_rds_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"), connection=ec2.Port.tcp(5432)
        )
        # Add my subnets
        for subnet in self.custom_vpc.private_subnets:
            self.covid_rds_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(subnet.ipv4_cidr_block), connection=ec2.Port.tcp(5432)
            )
        # Creating a database in vpc
        self.covid_rds = rds.DatabaseInstance(
            self,
            f"covid-{self.deploy_env.value}-rds",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_19
            ),
            database_name="covid_cases",
            instance_type=ec2.InstanceType("t3.micro"),
            vpc=self.custom_vpc,
            instance_identifier=f"rds-{self.deploy_env.value}-covid-db",
            port=5432,
            vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            subnet_group=rds.SubnetGroup(
                self,
                f"rds-{self.deploy_env.value}-subnet",
                description="place RDS on public subnet",
                vpc=self.custom_vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            ),
            parameter_group=self.covid_rds_parameter_group,
            security_groups=[self.covid_rds_sg],
            removal_policy=core.RemovalPolicy.DESTROY,
            **kwargs,
        )
