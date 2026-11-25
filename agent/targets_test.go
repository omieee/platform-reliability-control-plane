package agent

import (
	"slices"
	"testing"
)

func TestDefaultTargets(t *testing.T) {
	t.Run("check target values are correct", func(t *testing.T) {
		got := DefaultTargets()
		want := []string{"http://localhost:8000/health", "https://payments.example.com/health", "https://orders.example.com/health"}
		if !slices.Equal(got, want) {
			t.Errorf("Got: %q, wanted %q", got[:], want[:])
		}
	})

	t.Run("check if 0th index is self health", func(t *testing.T) {
		got := DefaultTargets()[0]
		want := "http://localhost:8000/health"
		if got != want {
			t.Errorf("Got: %q, wanted %q", got[:], want[:])
		}
	})
}
