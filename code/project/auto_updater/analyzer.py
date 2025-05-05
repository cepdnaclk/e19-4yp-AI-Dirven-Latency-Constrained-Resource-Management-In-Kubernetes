ates = {}
    
    for container, cpu in cpu_updates:
        if container not in combined_updates:
            combined_updates[container] = {}
        combined_updates[container]["cpu"] = cpu
        track_resource_allocation(container, cpu=cpu)
    
    for container, memory in memory_updates:
        if container not in combined_updates:
            combined_updates[container] = {}
        combined_updates[container]["memory"] = memory
        track_resource_allocation(container, memory=memory)
    
    return combined_updates