package agent

func DefaultTargets() []string {
	retValue := []string{"http://localhost:8000/health", "https://payments.example.com/health", "https://orders.example.com/health"}
	return retValue
}
