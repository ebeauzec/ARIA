# Deploy NetApp Data Classification in the cloud using the NetApp Console
Source: https://docs.netapp.com/us-en/bluexp-classification/task-deploy-cloud-compliance.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-data-classification/task-deploy-cloud-compliance.html (product renamed from "BlueXP Classification" to "NetApp Data Classification"). Page last updated 05/19/2026.

You can deploy NetApp Data Classification in the cloud with the NetApp Console. The Console deploys the Data Classification instance in the same cloud provider network as the Console agent.

Note that you can also [install Data Classification on a Linux host that has internet access](https://docs.netapp.com/us-en/data-services-data-classification/task-deploy-compliance-onprem.html). This type of installation may be a good option if you prefer to scan on-premises ONTAP systems using a Data Classification instance that's also located on premises — but this is not a requirement. The software functions exactly the same way regardless of which installation method you choose.

## Quick start

1. **Create a Console agent** — If you don't already have a Console agent, create one. See creating a Console agent in AWS, Azure, or GCP. You can also install the Console agent on-premises on a Linux host in your network or in the cloud.
2. **Prerequisites** — Ensure that your environment can meet the prerequisites. This includes outbound internet access for the instance, connectivity between the Console agent and Data Classification over port 443, and more.
3. **Deploy Data Classification** — Launch the installation wizard to deploy the Data Classification instance in the cloud.

## Create a Console agent

If you don't already have a Console agent, create a Console agent in your cloud provider (AWS, Azure, or GCP). In most cases, you probably have a Console agent set up before you attempt to activate Data Classification because most Console features require a Console agent, but there are cases where you'll need to set one up now.

There are some scenarios where you have to use a Console agent that's deployed in a specific cloud provider:

- When scanning data in Cloud Volumes ONTAP in AWS or Amazon FSx for ONTAP buckets, you use a Console agent in AWS.
- When scanning data in Cloud Volumes ONTAP in Azure or in Azure NetApp Files, you use a Console agent in Azure. For Azure NetApp Files, it must be deployed in the same region as the volumes you wish to scan.
- When scanning data in Cloud Volumes ONTAP in GCP, you use a Console agent in GCP.

On-prem ONTAP systems, NetApp file shares, and databases can be scanned when using any of these cloud Console agents.

You can also install the Console agent on-premises on a Linux host in your network or in the cloud. Some users planning to install Data Classification on-prem may also choose to install the Console agent on-premises.

There might be situations where you need to use multiple Console agents.

> **Tip:** Data Classification does not impose a limit on the amount of data it can scan. Each Console agent supports scanning and displaying 500 TiB of data. To scan more than 500 TiB of data, install another Console agent then deploy another Data Classification instance. The Console UI displays data from a single connector. For tips on viewing data from multiple Console agents, see Work with multiple Console agents.

### Government region support

Data Classification is supported when the Console agent is deployed in a Government region (AWS GovCloud, Azure Gov, or Azure DoD). When deployed in this manner, Data Classification has restrictions — see "Learn about deploying the Console agent in a Government region."

## Prerequisites

Review the following prerequisites to make sure that you have a supported configuration before you deploy Data Classification in the cloud. When you deploy Data Classification in the cloud, it's located in the same subnet as the Console agent.

### Enable outbound internet access from Data Classification

Data Classification requires outbound internet access. If your virtual or physical network uses a proxy server for internet access, ensure that the Data Classification instance has outbound internet access to contact the following endpoints. The proxy must be non-transparent — transparent proxies are not currently supported.

**Required endpoints for AWS**

| Endpoints | Purpose |
|---|---|
| https://api.console.netapp.com | Communication with the Console service, which includes NetApp accounts. |
| https://netapp-cloud-account.auth0.com, https://auth0.com | Communication with the Console website for centralized user authentication. |
| https://cloud-compliance-support-netapp.s3.us-west-2.amazonaws.com, https://hub.docker.com, https://auth.docker.io, https://registry-1.docker.io, https://index.docker.io/, https://dseasb33srnrn.cloudfront.net/, https://production.cloudflare.docker.com/ | Provides access to software images, manifests, and templates. |
| https://kinesis.us-east-1.amazonaws.com | Enables NetApp to stream data from audit records. |
| https://cognito-idp.us-east-1.amazonaws.com, https://cognito-identity.us-east-1.amazonaws.com, https://user-feedback-store-prod.s3.us-west-2.amazonaws.com, https://customer-data-production.s3.us-west-2.amazonaws.com | Enables Data Classification to access and download manifests and templates, and to send logs and metrics. |

**Required endpoints for Azure**

| Endpoints | Purpose |
|---|---|
| https://api.console.netapp.com | Communication with the Console service, which includes NetApp accounts. |
| https://netapp-cloud-account.auth0.com, https://auth0.com | Communication with the Console website for centralized user authentication. |
| https://support.compliance.api.console.netapp.com/, https://hub.docker.com, https://auth.docker.io, https://registry-1.docker.io, https://index.docker.io/, https://dseasb33srnrn.cloudfront.net/, https://production.cloudflare.docker.com/ | Provides access to software images, manifests, templates, and to send logs and metrics. |
| https://support.compliance.api.console.netapp.com/ | Enables NetApp to stream data from audit records. |

**Required endpoints for GCP**

| Endpoints | Purpose |
|---|---|
| https://api.console.netapp.com | Communication with the Console service, which includes NetApp accounts. |
| https://netapp-cloud-account.auth0.com, https://auth0.com | Communication with the Console website for centralized user authentication. |
| https://support.compliance.api.console.netapp.com/, https://hub.docker.com, https://auth.docker.io, https://registry-1.docker.io, https://index.docker.io/, https://dseasb33srnrn.cloudfront.net/, https://production.cloudflare.docker.com/ | Provides access to software images, manifests, templates, and to send logs and metrics. |
| https://support.compliance.api.console.netapp.com/ | Enables NetApp to stream data from audit records. |

### Ensure that Data Classification has the required permissions

Ensure that Data Classification has permissions to deploy resources and create security groups for the Data Classification instance:
- Google Cloud permissions
- AWS permissions
- Azure permissions

### Ensure that the Console agent can access Data Classification

Ensure connectivity between the Console agent and the Data Classification instance. The security group for the Console agent must allow inbound and outbound traffic over port 443 to and from the Data Classification instance. This connection enables deployment of the Data Classification instance and enables you to view information in the Compliance and Governance tabs. Data Classification is supported in Government regions in AWS and Azure.

Additional inbound/outbound security group rules are required for AWS and AWS GovCloud deployments, and for Azure and Azure Government deployments (see "Rules for the Console agent in AWS/Azure").

### Ensure you can keep Data Classification running

The Data Classification instance needs to stay on to continuously scan your data.

### Ensure web browser connectivity to Data Classification

After Data Classification is enabled, ensure that users access the Console interface from a host that has a connection to the Data Classification instance.

The Data Classification instance uses a private IP address to ensure that the indexed data isn't accessible to the internet. As a result, the web browser that you use to access the Console must have a connection to that private IP address. That connection can come from a direct connection to your cloud provider (for example, a VPN), or from a host that's inside the same network as the Data Classification instance.

### Check your vCPU limits

Ensure that your cloud provider's vCPU limit allows for the deployment of an instance with the necessary number of cores. You'll need to verify the vCPU limit for the relevant instance family in the region where the Console is running (see "The Data Classification instance" required instance types).

References:
- AWS documentation: Amazon EC2 service quotas
- Azure documentation: Virtual machine vCPU quotas
- Google Cloud documentation: Resource quotas

## Deploy Data Classification in the cloud

Follow these steps to deploy an instance of Data Classification in the cloud. The Console agent will deploy the instance in the cloud, and then install Data Classification software on that instance.

In regions where the default instance type isn't available, Data Classification runs on an alternate instance type.

### Deploy in AWS
1. From the main page of Data Classification, select **Deploy Classification On-Premises or Cloud**.
2. From the *Installation* page, select **Deploy > Deploy** to use the "Large" instance size and start the cloud deployment wizard.
3. The wizard displays progress as it goes through the deployment steps. When inputs are required or if it encounters issues, you are prompted.
4. When the instance is deployed and Data Classification is installed, select **Continue to configuration** to go to the *Configuration* page.

### Deploy in Azure
1. From the main page of Data Classification, select **Deploy Classification On-Premises or Cloud**.
2. Select **Deploy** to start the cloud deployment wizard.
3. The wizard displays progress as it goes through the deployment steps. It will stop and prompt for input if it runs into any issues.
4. When the instance is deployed and Data Classification is installed, select **Continue to configuration** to go to the *Configuration* page.

### Deploy in Google Cloud
1. From the main page of Data Classification, select **Governance > Classification**.
2. Select **Deploy Classification On-Premises or Cloud**.
3. Select **Deploy** to start the cloud deployment wizard.
4. The wizard displays progress as it goes through the deployment steps. It will stop and prompt for input if it runs into any issues.
5. When the instance is deployed and Data Classification is installed, select **Continue to configuration** to go to the *Configuration* page.

### Result

The Console deploys the Data Classification instance in your cloud provider. Upgrades to the Console agent and Data Classification software are automated as long as the instances have internet connectivity.

### What's Next

From the Configuration page you can select the data sources that you want to scan.
