#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GondolaSystem.generated.h"

class USplineComponent;
class UStaticMeshComponent;
class UTimelineComponent;
class UCurveFloat;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FGondolaDockedDelegate);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FGondolaDepartedDelegate);

/**
 * Cable car gondola that travels along a spline path between Millford and Maldek.
 * Place in level, shape the CablePath spline, and call SendGondola/ReturnGondola.
 */
UCLASS(Blueprintable)
class GAME_API AGondolaSystem : public AActor
{
	GENERATED_BODY()

public:

	AGondolaSystem();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	/** Send the gondola up to Maldek */
	UFUNCTION(BlueprintCallable, Category = "Gondola")
	void SendGondola();

	/** Return the gondola back to Millford */
	UFUNCTION(BlueprintCallable, Category = "Gondola")
	void ReturnGondola();

	/** Is the gondola currently docked at the platform? */
	UFUNCTION(BlueprintCallable, Category = "Gondola")
	bool IsDocked() const { return bDocked; }

	/** Is the gondola currently moving? */
	UFUNCTION(BlueprintCallable, Category = "Gondola")
	bool IsMoving() const { return bMoving; }

	/** Called when the gondola arrives and docks at the platform */
	UPROPERTY(BlueprintAssignable, Category = "Gondola")
	FGondolaDockedDelegate OnGondolaDocked;

	/** Called when the gondola departs the platform */
	UPROPERTY(BlueprintAssignable, Category = "Gondola")
	FGondolaDepartedDelegate OnGondolaDeparted;

protected:

	/** The spline representing the cable path from Millford to Maldek */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USplineComponent* CablePath;

	/** The gondola mesh */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* GondolaMesh;

	/** How long the gondola takes to travel one way (seconds) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola", meta = (ClampMin = 1.0))
	float TravelTime = 30.0f;

	/** How long the gondola waits at Maldek before returning (seconds) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola", meta = (ClampMin = 0.0))
	float WaitTimeAtMaldek = 180.0f;

	/** Current progress along the spline (0 = Millford, 1 = Maldek) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Gondola")
	float CurrentAlpha = 0.0f;

private:

	/** Update the gondola position along the spline */
	void UpdateGondolaPosition();

	/** Called when the gondola reaches its destination */
	void OnReachedDestination();

	/** Direction: +1 = ascending to Maldek, -1 = descending to Millford */
	float Direction = 0.0f;

	bool bMoving = false;
	bool bDocked = true;
	bool bWaitingAtMaldek = false;

	/** Timer for waiting at Maldek */
	FTimerHandle MaldekWaitTimer;
};
