terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.66"
    }
  }
}

# Hetzner Cloud provider
# Token HCLOUD_TOKEN environment variable orqali olinadi
provider "hcloud" {}

# Ubuntu server
resource "hcloud_server" "devops_server" {
  name        = "devops-server"
  image       = "ubuntu-24.04"
  server_type = "cx23"
  location    = "hel1"

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
}

# Serverning public IPv4 manzilini chiqarish
output "server_ipv4" {
  value = hcloud_server.devops_server.ipv4_address
}
