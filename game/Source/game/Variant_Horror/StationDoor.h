#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationDoor.generated.h"

class UStaticMeshComponent;
class UBoxComponent;
class UTextRenderComponent;
class APlayerController;
class UMaterialInstanceDynamic;

/** Hinged station door. Locked doors never change their collision or opening target. */
UCLASS(Blueprintable)
class GAME_API AStationDoor : public AActor
{
 GENERATED_BODY()
public:
 AStationDoor();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UFUNCTION(BlueprintCallable, Category="Door") bool TryInteract();
 UFUNCTION(BlueprintCallable, Category="Door") bool Unlock();
 UFUNCTION(BlueprintCallable, Category="Door") bool SubmitCode(const FString& Code);
 UFUNCTION(BlueprintPure, Category="Door") bool IsLocked() const { return bLocked; }
 UFUNCTION(BlueprintPure, Category="Door") float GetOpenAngle() const { return CurrentAngle; }
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<USceneComponent> DoorRoot;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<USceneComponent> Hinge;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Leaf;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Glass;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> FixedHardware;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> Keypad;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> InteriorElectronics;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UStaticMeshComponent> ElectronicStrike;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Door") TObjectPtr<UBoxComponent> LeafCollision;
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UTextRenderComponent> Prompt;
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UTextRenderComponent> KeypadDisplay;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bHasKeypad=false;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bLocked=false;
 /** Empty by default: a level designer must deliberately configure a code. */
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") FString AccessCode;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door") float OpenAngle=105.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="10")) float DegreesPerSecond=85.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="50")) float InteractionDistance=220.f;
private:
 float CurrentAngle=0.f;
 float TargetAngle=0.f;
 float FeedbackSeconds=0.f;
 bool bObstructed=false;
 bool bEnteringCode=false;
 bool bCodeRejected=false;
 FString EnteredCode;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> StatusMaterial;
 bool HasFocus(APlayerController* Controller) const;
 bool CanOccupyAngle(float Angle) const;
 void RefreshLockVisuals();
};
