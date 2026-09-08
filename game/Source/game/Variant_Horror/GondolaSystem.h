#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GondolaSystem.generated.h"

class USplineComponent;
class UStaticMeshComponent;
class UTimelineComponent;
class UCurveFloat;
class UWidgetComponent;
class UAudioComponent;
class USoundBase;
class UBoxComponent;

UENUM(BlueprintType)
enum class EGondolaDoorPhase : uint8 { Closed, Settling, Opening, Open, Closing, Latching };

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

	UFUNCTION(BlueprintCallable, Category = "Gondola")
	void BeginArrival();
	UFUNCTION(BlueprintPure, Category = "Gondola")
	float GetRouteDistance() const { return RouteDistance; }
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TObjectPtr<UStaticMeshComponent> DoorLeft;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TObjectPtr<UStaticMeshComponent> DoorRight;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TObjectPtr<UStaticMeshComponent> DoorPinion;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TArray<TObjectPtr<UStaticMeshComponent>> DoorRollers;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TObjectPtr<UBoxComponent> DoorLeftCollision;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	TObjectPtr<UBoxComponent> DoorRightCollision;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gondola|Doors")
	TObjectPtr<USoundBase> DoorOpenSound;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gondola|Doors")
	TObjectPtr<USoundBase> DoorCloseSound;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	EGondolaDoorPhase DoorPhase = EGondolaDoorPhase::Closed;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Gondola|Doors")
	float DoorOpenFraction = 0.f;
	UFUNCTION(BlueprintPure, Category="Gondola|Doors")
	bool IsDeparturePending() const { return bDepartureRequested; }
	/** Finished cabin pieces and lights, attached with authored dock offsets. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Assembly")
	TArray<TObjectPtr<AActor>> CabinParts;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Terminal")
	TObjectPtr<AActor> FarBoardingBridge;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Terminal")
	TArray<TObjectPtr<AActor>> FarBridgeParts;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Terminal")
	FVector FarBridgeParked = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Terminal")
	FVector FarBridgeDeployed = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Arrival")
	bool bStageFirstArrival = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Arrival")
	FVector ArrivalTriggerLocation = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Arrival", meta = (ClampMin = "100"))
	float ArrivalTriggerRadius = 4300.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Arrival", meta = (ClampMin = "0"))
	float FirstArrivalDistance = 3048.f;
	/** Speeds/distances in centimetres/seconds. TravelTime is a legacy fallback. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Motion", meta = (ClampMin = "0"))
	float CruiseSpeed = 350.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Motion", meta = (ClampMin = "1"))
	float ApproachSpeed = 80.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Motion", meta = (ClampMin = "1"))
	float Acceleration = 40.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Motion", meta = (ClampMin = "0"))
	float SlowZoneDistance = 3500.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola|Motion")
	FRotator CabinDockRotation = FRotator::ZeroRotator;

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
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UWidgetComponent> DeparturePrompt;

	/** How long the gondola takes to travel one way (seconds) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gondola", meta = (ClampMin = 1.0))
	float TravelTime = 420.0f;

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
	bool bArrivalPending = false;
	float RouteDistance = 0.f;
	float CurrentSpeed = 0.f;
	float DockRouteYaw = 0.f;
	void SetCabinHidden(bool bHideCabin);
	bool bReturnRequested = false;
	void UpdateBoardingBridge(float DeltaTime);
	UPROPERTY()
	TObjectPtr<UAudioComponent> DoorAudio;
	void UpdateDoors(float DeltaTime);
	void CreateDoorComponents();
	void ApplyDoorPose();
	void StartDoorOpening();
	void RequestDeparture(float TravelDirection);
	void StartDeparture();
	bool HasSlidingDoors() const;
	bool DoorwayOccupied() const;
	bool BridgeOccupied() const;
	bool LandingReady() const;
	void PlayDoorRecording(USoundBase* Sound);
	bool bDepartureRequested = false;
	float RequestedDirection = 0.f;
	float DoorPhaseTime = 0.f;
	float DoorTravel = 0.f;

	/** Timer for waiting at Maldek */
	FTimerHandle MaldekWaitTimer;
};
