#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationDoor.generated.h"

class UStaticMeshComponent;
class UBoxComponent;
class UTextRenderComponent;
class APlayerController;
class APawn;
class UMaterialInstanceDynamic;
class UCameraComponent;
class UMeshComponent;
class UAudioComponent;
class USoundBase;
class SWidget;
class STextBlock;

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
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 UFUNCTION(BlueprintCallable, Category="Door") void CancelKeypadInteraction();
 UFUNCTION(BlueprintPure, Category="Door") bool IsUsingKeypad() const { return bEnteringCode; }
 UFUNCTION(BlueprintPure, Category="Door") FVector GetKeypadButtonWorldPosition(int32 Index) const;
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
 UPROPERTY(VisibleAnywhere, Category="Door") TObjectPtr<UCameraComponent> KeypadCamera;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bHasKeypad=false;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") bool bLocked=false;
 /** Empty by default: a level designer must deliberately configure a code. */
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door") FString AccessCode;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door") float OpenAngle=105.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="10")) float DegreesPerSecond=85.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Door", meta=(ClampMin="50")) float InteractionDistance=220.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ButtonSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ClearSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> ConfirmSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> RejectSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> UnlatchSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> MovementSound;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Door|Audio") TObjectPtr<USoundBase> CloseSound;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> EventAudio;
 UPROPERTY(VisibleAnywhere, Category="Door|Audio") TObjectPtr<UAudioComponent> MotionAudio;
private:
 TSharedPtr<SWidget> HintWidget;
 TSharedPtr<STextBlock> HintAction,HintDetail;
 void ShowDoorHint(bool bVisible,const FString& Action=FString(),const FString& Detail=FString());
 void PlayDoorSound(USoundBase* Sound,bool bKeypad=false);
 float CurrentAngle=0.f;
 float TargetAngle=0.f;
 float FeedbackSeconds=0.f;
 bool bObstructed=false;
 bool bEnteringCode=false;
 bool bCodeRejected=false;
 FString EnteredCode;
 float KeypadBlendRemaining=0;
 TWeakObjectPtr<APlayerController> KeypadController;
 TWeakObjectPtr<AActor> PreviousViewTarget;
 TWeakObjectPtr<APawn> PreviousPawn;
 TArray<TWeakObjectPtr<UMeshComponent>> HiddenPlayerMeshes;
 bool bPreviousMouseCursor=false;
 uint8 PreviousMovementMode=0, PreviousCustomMovementMode=0;
 bool BeginKeypadInteraction(APlayerController* Controller);
 void EndKeypadInteraction(bool bBlend);
 void PressKeypadButton(int32 Index);
 int32 HoveredKeypadButton(APlayerController* Controller) const;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> StatusMaterial;
 bool HasFocus(APlayerController* Controller) const;
 bool CanOccupyAngle(float Angle) const;
 void RefreshLockVisuals();
};
