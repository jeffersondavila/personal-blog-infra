output "id_de_vpc" {
  value       = aws_vpc.this.id
  description = "ID de la VPC dedicada."
}

output "ids_de_subredes" {
  value       = [for clave in sort(keys(var.subredes)) : aws_subnet.privada[clave].id]
  description = "Subredes privadas, en el orden estable de sus claves (a, b)."
}

output "zonas_de_subredes" {
  value       = { for clave, subred in aws_subnet.privada : clave => subred.availability_zone }
  description = "Nombre de la AZ de cada subred. Es lo que acepta `aws_db_instance`."
}

output "id_sg_lambda" {
  value       = aws_security_group.lambda.id
  description = "Grupo de la Lambda de aplicacion. Task/032 DEBE adjuntarlo explicitamente: nunca el grupo por omision de la VPC."
}

output "id_sg_rds" {
  value       = aws_security_group.rds.id
  description = "Grupo de la base de datos: el UNICO que lleva la instancia."
}

output "id_sg_admin" {
  value       = aws_security_group.admin.id
  description = "Grupo de la ejecutora privada de D-24. H-031-5 DEBE adjuntarlo explicitamente: nunca el grupo por omision de la VPC."
}

output "id_endpoint_s3" {
  value       = aws_vpc_endpoint.s3.id
  description = "Gateway endpoint de S3."
}

output "prefix_list_s3" {
  value       = aws_vpc_endpoint.s3.prefix_list_id
  description = "Prefix list administrada de S3 en la region."
}

# Contrato de VERIFICACION, como `configuracion_efectiva` del modulo de
# almacenamiento: permite a las pruebas offline y al readback afirmar sobre lo
# realmente declarado sin alcanzar recursos internos. No lleva ningun secreto.
output "configuracion_efectiva" {
  description = "Configuracion declarada de la red, para pruebas y readback."
  value = {
    cidr                  = aws_vpc.this.cidr_block
    dns_support           = aws_vpc.this.enable_dns_support
    dns_hostnames         = aws_vpc.this.enable_dns_hostnames
    ipv6                  = aws_vpc.this.assign_generated_ipv6_cidr_block
    subredes              = { for clave, subred in aws_subnet.privada : clave => { cidr = subred.cidr_block, zona_id = subred.availability_zone_id, ip_publica = subred.map_public_ip_on_launch } }
    tipo_de_endpoint      = aws_vpc_endpoint.s3.vpc_endpoint_type
    servicio_del_endpoint = aws_vpc_endpoint.s3.service_name
    politica_del_endpoint = aws_vpc_endpoint.s3.policy
    # `route_table_ids` es un set de IDs que solo se conocen tras el apply: su
    # numero se comprueba en el readback, no en el plan.
    tablas_del_endpoint = length(aws_vpc_endpoint.s3.route_table_ids)
    reglas = {
      rds_desde_lambda = { origen = aws_vpc_security_group_ingress_rule.rds_desde_lambda.referenced_security_group_id, puerto = aws_vpc_security_group_ingress_rule.rds_desde_lambda.from_port, cidr = aws_vpc_security_group_ingress_rule.rds_desde_lambda.cidr_ipv4 }
      rds_desde_admin  = { origen = aws_vpc_security_group_ingress_rule.rds_desde_admin.referenced_security_group_id, puerto = aws_vpc_security_group_ingress_rule.rds_desde_admin.from_port, cidr = aws_vpc_security_group_ingress_rule.rds_desde_admin.cidr_ipv4 }
      lambda_a_rds     = { destino = aws_vpc_security_group_egress_rule.lambda_a_rds.referenced_security_group_id, puerto = aws_vpc_security_group_egress_rule.lambda_a_rds.from_port, cidr = aws_vpc_security_group_egress_rule.lambda_a_rds.cidr_ipv4 }
      lambda_a_s3      = { prefix_list = aws_vpc_security_group_egress_rule.lambda_a_s3.prefix_list_id, puerto = aws_vpc_security_group_egress_rule.lambda_a_s3.from_port, cidr = aws_vpc_security_group_egress_rule.lambda_a_s3.cidr_ipv4 }
      admin_a_rds      = { destino = aws_vpc_security_group_egress_rule.admin_a_rds.referenced_security_group_id, puerto = aws_vpc_security_group_egress_rule.admin_a_rds.from_port, cidr = aws_vpc_security_group_egress_rule.admin_a_rds.cidr_ipv4 }
    }
    grupos = {
      lambda = aws_security_group.lambda.id
      rds    = aws_security_group.rds.id
      admin  = aws_security_group.admin.id
    }
  }
}
