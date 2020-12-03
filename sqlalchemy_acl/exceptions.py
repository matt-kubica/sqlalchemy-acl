class ACLException(Exception):
	pass

class ACLModelNotValid(ACLException):
	pass

class UserNotValid(ACLModelNotValid):
	pass

class ACLEntryNotValid(ACLModelNotValid):
	pass

class AccessLevelNotValid(ACLModelNotValid):
	pass

class ListRequired(ACLException):
	pass