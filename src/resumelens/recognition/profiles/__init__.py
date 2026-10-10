# Stage 3 - Collects the patterns of the 4 profiles in a single dictionary.
# The keys are the same ones used in Stage 2 (PROFILE_ORDER).
 
from .full_stack import PROFILE as FULL_STACK
from .machine_learning import PROFILE as MACHINE_LEARNING
from .ai_engineer import PROFILE as AI_ENGINEER
from .cloud_engineer import PROFILE as CLOUD_ENGINEER
 
PROFILES = {
    "full_stack": FULL_STACK,
    "machine_learning": MACHINE_LEARNING,
    "ai_engineer": AI_ENGINEER,
    "cloud_engineer": CLOUD_ENGINEER,
}
 
















