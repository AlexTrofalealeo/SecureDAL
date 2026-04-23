from src.tamper_operator import TamperOperator

# Initialize the operator for postgreSQL
op = TamperOperator(
    "postgresql",
    connection_string="postgresql://tamper_user:password@localhost:5432/tamper",
    table="opendal_storage"
)

print("write: ", op.capability().write)
print("write_can_multi: ", op.capability().write_can_multi)
print("write_can_empty: ", op.capability().write_can_empty)
print("write_can_append: ", op.capability().write_can_append)
print("write_with_content_type: ", op.capability().write_with_content_type)
print("write_with_content_disposition: ", op.capability().write_with_content_disposition)
print("write_with_content_encoding: ", op.capability().write_with_content_encoding)
print("write_with_cache_control: ", op.capability().write_with_cache_control)
print("write_with_if_match: ", op.capability().write_with_if_match)
print("write_with_if_none_match: ", op.capability().write_with_if_none_match)
print("write_with_if_not_exists: ", op.capability().write_with_if_not_exists)
print("write_with_user_metadata: ", op.capability().write_with_user_metadata)
print("write_multi_max_size: ", op.capability().write_multi_max_size)
print("write_multi_min_size: ", op.capability().write_multi_min_size)
print("write_total_max_size: ", op.capability().write_total_max_size)