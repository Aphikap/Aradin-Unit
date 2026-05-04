output "namespace_name" {
  description = "Name of the namespace created for Aradin Converter"
  value       = kubernetes_namespace.aradin.metadata[0].name
}
