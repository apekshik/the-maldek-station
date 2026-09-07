#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SurfaceFootstepComponent.generated.h"

class ACharacter;
class USoundBase;

/** Distance-driven first-person footsteps. Surface IDs are configured in DefaultEngine.ini. */
UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class GAME_API USurfaceFootstepComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	USurfaceFootstepComponent();
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")
	TArray<TObjectPtr<USoundBase>> SoilSteps;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")
	TArray<TObjectPtr<USoundBase>> GravelSteps;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")
	TArray<TObjectPtr<USoundBase>> MetalSteps;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")
	TArray<TObjectPtr<USoundBase>> ConcreteSteps;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")
	TArray<TObjectPtr<USoundBase>> WoodSteps;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps", meta=(ClampMin="0", ClampMax="2"))
	float Volume = 0.65f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps", meta=(ClampMin="50"))
	float WalkStepDistance = 145.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps", meta=(ClampMin="50"))
	float RunStepDistance = 190.0f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category="Footsteps|Diagnostics")
	int32 FootstepCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category="Footsteps|Diagnostics")
	int32 LastSurface = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category="Footsteps|Diagnostics")
	FString LastFloorMaterial;

private:
	UPROPERTY(Transient)
	TObjectPtr<ACharacter> Character;
	FVector PreviousLocation = FVector::ZeroVector;
	float DistanceSinceStep = 0.0f;
	TMap<int32, int32> PreviousSamples;
	void PlayStep(float Speed);
};
