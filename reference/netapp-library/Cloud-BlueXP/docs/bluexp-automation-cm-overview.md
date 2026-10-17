# Learn about the ONTAP management REST APIs
Source: https://docs.netapp.com/us-en/bluexp-automation/cm/overview.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/console-automation/cm/overview.html (BlueXP automation docs moved under "console-automation").

Last updated: 12/19/2025

ONTAP management is composed of multiple related REST APIs that enable you to administer your cloud-based and on-premises ONTAP storage resources. Using the REST APIs, you can perform many different operations, including managing Cloud Volumes ONTAP single-node and high availability (HA) resources (ONTAP instances running on the public cloud providers), on-premises ONTAP cluster resources (including AFF/FAS systems), configure cloud providers, support the NetApp Console account resources, and more.

The different types of resources supporting these operations can be broadly categorized as follows:

- **Administrative resources** — These resources are used to set up and configure the Console environment.
- **Auditing resources** — You can view the details about the Console operations that have been initiated or are active.
- **Authentication resources** — You need to authenticate using an account for the Console to run the API operations.
- **System resources** — These resources represent available deployment environments, including Cloud Volumes ONTAP single-node and HA configurations as well as on-premises ONTAP clusters.

Each resource is accessible through a set of API endpoints.

## Cloud Volumes ONTAP operations

Cloud Volumes ONTAP API is widely used by developers to create and administer Cloud Volumes ONTAP system resources, add aggregates, and volumes to Cloud Volumes ONTAP instances. The Cloud Volumes ONTAP REST API calls vary depending on the different cloud providers. Also, there are slight variations among the Cloud Volumes ONTAP API calls used for single-node versus HA configurations.

## On-premises ONTAP operations

You can discover and manage the on-premises ONTAP resources by using the on-premises REST API calls. In addition, you can also perform various management operations, such as add an ONTAP cluster as a system resource, add volumes, and perform other related actions.

## API workflows

ONTAP management supports many different workflows. Each workflow is focused on performing a specific administrative task. There are three major sets of workflows:

- [Cloud Volumes ONTAP workflows](https://docs.netapp.com/us-en/console-automation/cm/wf_cvo_before.html)
- [On-premises ONTAP workflows](https://docs.netapp.com/us-en/console-automation/cm/wf_onprem_before.html)
- [Common workflows](https://docs.netapp.com/us-en/console-automation/cm/wf_common_before.html)

See [Workflows processes](https://docs.netapp.com/us-en/console-automation/cm/workflow_processes.html) to learn more about the workflows and their common characteristics before using a specific API.

## API reference

You can use the [API reference](https://docs.netapp.com/us-en/console-automation/cm/api_reference.html) documentation when working with ONTAP management. It includes specific reference information for each of the available operations.
