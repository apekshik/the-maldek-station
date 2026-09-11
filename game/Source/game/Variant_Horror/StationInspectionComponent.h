#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StationInspectionComponent.generated.h"

class AStationInspectable;
class APlayerController;
class ACameraActor;
class UPrimitiveComponent;
class UMeshComponent;
class SWidget;

UENUM(BlueprintType)
enum class EStationInspectionPhase : uint8 { Idle, PickingUp, Inspecting, Returning };

/** Local controller owns one inspection session; input locks remain held through the return blend. */
UCLASS(ClassGroup=(Station), meta=(BlueprintSpawnableComponent))
class GAME_API UStationInspectionComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UStationInspectionComponent();
 virtual void TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* Function) override;
 virtual void EndPlay(EEndPlayReason::Type Reason) override;
 UFUNCTION(BlueprintCallable, Category="Inspection") bool BeginInspection(AStationInspectable* Object);
 UFUNCTION(BlueprintCallable, Category="Inspection") void ReturnObject();
 /** Immediate restoration for teleport, unpossess, level teardown, or another camera taking over. */
 UFUNCTION(BlueprintCallable, Category="Inspection") void CancelInspection();
 UFUNCTION(BlueprintCallable, Category="Inspection") void ResetPose();
 UFUNCTION(BlueprintCallable, Category="Inspection") void RotateObject(float Horizontal,float Vertical,float Roll=0);
 UFUNCTION(BlueprintCallable, Category="Inspection") void ZoomObject(float Steps);
 /** Button events preserve the final delta even for a drag completed between ticks. */
 void HandlePointerButton(bool bPressed);
 UFUNCTION(BlueprintPure, Category="Inspection") bool IsInspectingObject() const {return Phase!=EStationInspectionPhase::Idle;}
 UFUNCTION(BlueprintPure, Category="Inspection") bool HasFocusedObject() const {return FindFocusedObject()!=nullptr;}
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Inspection") EStationInspectionPhase Phase=EStationInspectionPhase::Idle;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection", meta=(ClampMin="50",ClampMax="400")) float Reach=220;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection", meta=(ClampMin="0.1",ClampMax="2")) float BlendSeconds=.38f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection", meta=(ClampMin="0.05",ClampMax="2")) float RotationSensitivity=.3f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Inspection", meta=(ClampMin="35",ClampMax="80")) float InspectionFOV=55;
private:
 struct FBodyState
 {
  TWeakObjectPtr<UPrimitiveComponent> Body;
  ECollisionEnabled::Type Collision=ECollisionEnabled::NoCollision;
  bool bSimulating=false,bGravity=false,bAwake=false;
  FVector Velocity=FVector::ZeroVector,AngularVelocity=FVector::ZeroVector;
 };
 TArray<FBodyState> Bodies;
 TArray<TWeakObjectPtr<UMeshComponent>> HiddenMeshes;
 TWeakObjectPtr<AStationInspectable> FocusedObject,HeldObject;
 TWeakObjectPtr<APawn> SavedPawn;
 TWeakObjectPtr<AActor> SavedView;
 TWeakObjectPtr<USceneComponent> SavedParent;
 FName SavedSocket;
 UPROPERTY(Transient) TObjectPtr<ACameraActor> InspectionCamera;
 FTransform OriginalWorld,OriginalRelative,ReturnStart;
 FVector LocalCenter=FVector::ZeroVector;
 FQuat TargetRotation=FQuat::Identity,CurrentRotation=FQuat::Identity,HomeRotation=FQuat::Identity;
 float Elapsed=0,Distance=0,TargetDistance=0,HomeDistance=0,MinimumDistance=0,MaximumDistance=0;
 uint8 SavedMovementMode=0,SavedCustomMode=0;
 bool bMovementSaved=false,bLocksHeld=false;
 bool bPointerDragging=false,bSavedMouseCursor=false;
 uint8 SavedCursor=0;
 FVector2D LastPointerPosition=FVector2D::ZeroVector;
 uint64 InputSuppressedFrame=0;
 TSharedPtr<SWidget> Overlay;
 APlayerController* Player() const;
 bool CanSearch() const;
 AStationInspectable* FindFocusedObject() const;
 FTransform ReturnTransform() const;
 FTransform HeldTransform() const;
 void Finish(bool bPlaySound);
 void CreateOverlay();
 void UpdatePointerDrag();
 FVector2D FocusPromptPosition() const;
 FText OverlayTitle() const;
 FText OverlayDetail() const;
};
